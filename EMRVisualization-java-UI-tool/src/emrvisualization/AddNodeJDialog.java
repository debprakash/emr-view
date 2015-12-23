/*
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details:
 * http://www.gnu.org/licenses/gpl.txt
 */
/*
 * AddNodeJDialog.java
 *
 * Created on Dec 22, 2009, 1:23:10 PM
 */
package emrvisualization;

import emr.data.EMRNode;
import emr.util.SearchIndexBuilder;
import emrvisualization.util.VisualUtils;
import java.io.IOException;
import java.util.HashSet;
import java.util.Vector;
import javax.swing.JTable;
import javax.swing.ListSelectionModel;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import javax.swing.event.TreeSelectionEvent;
import javax.swing.event.TreeSelectionListener;
import javax.swing.table.AbstractTableModel;
import javax.swing.table.TableModel;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.TreeSelectionModel;
import org.apache.lucene.queryParser.ParseException;
import org.jdesktop.application.Action;

/**
 *
 * @author debprakash
 */
public class AddNodeJDialog extends javax.swing.JDialog {

    SearchIndexBuilder searcher;
    Vector<EMRNode> results = new Vector<EMRNode>();
    ResultTableModel resultsDataModel = new ResultTableModel();
    boolean selected = false;
    EMRNode selectedID = null;
    SelectionListener listener = null;

    public TableModel getResultTableModel() {
        return resultsDataModel;
    }

    /** Creates new form AddNodeJDialog */
    public AddNodeJDialog(java.awt.Frame parent) {
        super(parent);
        initComponents();
        try {
            searcher = new SearchIndexBuilder();
            searcher.openIndex();
        } catch (IOException ex) {
            System.err.println("Exception : " + ex);
            ex.printStackTrace();
        } catch (ParseException ex) {
            System.err.println("Exception : " + ex);
        }
        VisualUtils.setColumnSizes(jTableResults, new double[]{0.2, 0.8});
        jTableResults.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        listener = new SelectionListener(jTableResults);
        jTableResults.getSelectionModel().addListSelectionListener(listener);


        xMLTree1.getSelectionModel().setSelectionMode(TreeSelectionModel.SINGLE_TREE_SELECTION);
        xMLTree1.addTreeSelectionListener(new TreeSelectionListener() {

            public void valueChanged(TreeSelectionEvent e) {
                DefaultMutableTreeNode node = (DefaultMutableTreeNode) xMLTree1.getLastSelectedPathComponent();

                if (node == null) {
                    return;
                }

                EMRNode nodeInfo = (EMRNode) node.getUserObject();
                /* React to the node selection. */
                jTextArea1.setText(nodeInfo.getId() + " " + nodeInfo.getName()
                        + ":-\n" + nodeInfo.getDesc());
                String labeltxt = (nodeInfo.getId() + " " + nodeInfo.getName());
                if (labeltxt.length() > 40) {
                    labeltxt = labeltxt.substring(0, 37) + "...";
                }
                jLabelSelection.setText(labeltxt);
                jLabelSelection.setToolTipText(nodeInfo.getId() + " " + nodeInfo.getName());
                selectedID = nodeInfo;
            }
        });


        jTextFieldFind.getDocument().addDocumentListener(new DocumentListener() {

            public void insertUpdate(DocumentEvent e) {
                search();
            }

            public void removeUpdate(DocumentEvent e) {
                search();
            }

            public void changedUpdate(DocumentEvent e) {
                throw new UnsupportedOperationException("Not supported yet.");
            }
        });

    }

    void setAvailableCodes(HashSet<String> availableCodes) {
        searcher.createAvailableCodesFilter(availableCodes);
    }

    public class SelectionListener implements ListSelectionListener {

        JTable table;
        int prev = -1;

        // It is necessary to keep the table since it is not possible
        // to determine the table from the event's source
        SelectionListener(JTable table) {
            this.table = table;
        }

        public void valueChanged(ListSelectionEvent e) {
            // If cell selection is enabled, both row and column change events are fired
            if (e.getSource() == table.getSelectionModel()
                    && table.getRowSelectionAllowed()
                    && !e.getValueIsAdjusting()) {
                // Column selection changed
                int first = e.getFirstIndex();
                int last = e.getLastIndex();
                System.out.println("first: " + first + " last: " + last);
                int next = last;
                //if (prev == first) next = last;
                if (prev == last) next = first;
                if (next >= 0 && next < results.size()) {
                    EMRNode nodeInfo = results.get(next);
                    jTextArea1.setText(nodeInfo.getId() + " " + nodeInfo.getName()
                            + ":-\n" + nodeInfo.getDesc());
                    String labeltxt = (nodeInfo.getId() + " " + nodeInfo.getName());
                    if (labeltxt.length() > 40) {
                        labeltxt = labeltxt.substring(0, 37) + "...";
                    }
                    jLabelSelection.setText(labeltxt);
                    jLabelSelection.setToolTipText(nodeInfo.getId() + " " + nodeInfo.getName());
                    selectedID = nodeInfo;

                    AddNodeJDialog.this.xMLTree1.gotoNode(nodeInfo.getId());
                    prev = next;
                }
            }
        }
    }

    class ResultTableModel extends AbstractTableModel {

        public void updateResults() {

            int prev_size = results.size();
            results.clear();
            if (prev_size == 0) {
                prev_size++;
            }
            fireTableRowsDeleted(0, prev_size - 1);
            listener.prev = -1;
            try {
                String keyword = jTextFieldFind.getText();
                
                if (keyword.length() > 0) {
                    int found = searcher.search(keyword, results);
                    jLabelHits.setText("Number of hits = " + found);
                    int new_size = results.size();
                    if (new_size == 0) {
                        new_size++;
                    }
                    fireTableRowsInserted(0, new_size - 1);
                } else {
                    jLabelHits.setText("Number of hits = ");
                }

            } catch (IOException ex) {
                System.err.println("Exception " + ex);
                ex.printStackTrace();
            } catch (ParseException ex) {
                System.err.println("Exception " + ex);
                ex.printStackTrace();
            }

        }

        public int getRowCount() {
            return results.size();
        }

        public int getColumnCount() {
            return 2;
        }

        public Object getValueAt(int rowIndex, int columnIndex) {
            switch (columnIndex) {
                case 0:
                    return results.get(rowIndex).getId();
                case 1:
                    return results.get(rowIndex).getName();
            }
            return "";
        }

        @Override
        public Class<?> getColumnClass(int columnIndex) {
            return String.class;
        }

        @Override
        public String getColumnName(int column) {
            switch (column) {
                case 0:
                    return "ICD Code";
                case 1:
                    return "Description";
                default:
                    return null;
            }
        }

        @Override
        public boolean isCellEditable(int rowIndex, int columnIndex) {
            return false;
        }
    };

    public boolean isSelected() {
        return selected;
    }

    public EMRNode getSelectedID() {
        return selectedID;
    }

    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        jLabel1 = new javax.swing.JLabel();
        jTextFieldFind = new javax.swing.JTextField();
        jButtonAdd = new javax.swing.JButton();
        jScrollPane1 = new javax.swing.JScrollPane();
        jTableResults = new javax.swing.JTable();
        jButtonCancel = new javax.swing.JButton();
        jLabel2 = new javax.swing.JLabel();
        jScrollPane4 = new javax.swing.JScrollPane();
        jTextArea1 = new javax.swing.JTextArea();
        jLabel3 = new javax.swing.JLabel();
        jScrollPane2 = new javax.swing.JScrollPane();
        xMLTree1 = new emr.util.XMLTree();
        jLabelSelection = new javax.swing.JLabel();
        jLabelHits = new javax.swing.JLabel();

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);
        org.jdesktop.application.ResourceMap resourceMap = org.jdesktop.application.Application.getInstance(emrvisualization.EMRVisualizationApp.class).getContext().getResourceMap(AddNodeJDialog.class);
        setTitle(resourceMap.getString("Form.title")); // NOI18N
        setModal(true);
        setName("Form"); // NOI18N
        setResizable(false);

        jLabel1.setText(resourceMap.getString("jLabel1.text")); // NOI18N
        jLabel1.setName("jLabel1"); // NOI18N

        jTextFieldFind.setText(resourceMap.getString("jTextFieldFind.text")); // NOI18N
        javax.swing.ActionMap actionMap = org.jdesktop.application.Application.getInstance(emrvisualization.EMRVisualizationApp.class).getContext().getActionMap(AddNodeJDialog.class, this);
        jTextFieldFind.setAction(actionMap.get("search")); // NOI18N
        jTextFieldFind.setName("jTextFieldFind"); // NOI18N

        jButtonAdd.setAction(actionMap.get("closeAddDialog")); // NOI18N
        jButtonAdd.setText(resourceMap.getString("jButtonAdd.text")); // NOI18N
        jButtonAdd.setName("jButtonAdd"); // NOI18N

        jScrollPane1.setName("jScrollPane1"); // NOI18N

        jTableResults.setModel(getResultTableModel());
        jTableResults.setName("jTableResults"); // NOI18N
        jScrollPane1.setViewportView(jTableResults);

        jButtonCancel.setAction(actionMap.get("cancel")); // NOI18N
        jButtonCancel.setText(resourceMap.getString("jButtonCancel.text")); // NOI18N
        jButtonCancel.setName("jButtonCancel"); // NOI18N

        jLabel2.setText(resourceMap.getString("jLabel2.text")); // NOI18N
        jLabel2.setName("jLabel2"); // NOI18N

        jScrollPane4.setName("jScrollPane4"); // NOI18N

        jTextArea1.setColumns(20);
        jTextArea1.setEditable(false);
        jTextArea1.setLineWrap(true);
        jTextArea1.setRows(5);
        jTextArea1.setWrapStyleWord(true);
        jTextArea1.setName("jTextArea1"); // NOI18N
        jScrollPane4.setViewportView(jTextArea1);

        jLabel3.setText(resourceMap.getString("jLabel3.text")); // NOI18N
        jLabel3.setName("jLabel3"); // NOI18N

        jScrollPane2.setName("jScrollPane2"); // NOI18N

        xMLTree1.setName("xMLTree1"); // NOI18N
        xMLTree1.setRootVisible(false);
        xMLTree1.setShowsRootHandles(true);
        jScrollPane2.setViewportView(xMLTree1);

        jLabelSelection.setText(resourceMap.getString("jLabelSelection.text")); // NOI18N
        jLabelSelection.setName("jLabelSelection"); // NOI18N

        jLabelHits.setText(resourceMap.getString("jLabelHits.text")); // NOI18N
        jLabelHits.setName("jLabelHits"); // NOI18N

        org.jdesktop.layout.GroupLayout layout = new org.jdesktop.layout.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(layout.createSequentialGroup()
                .addContainerGap()
                .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
                    .add(jScrollPane1, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 297, Short.MAX_VALUE)
                    .add(jScrollPane4, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 297, Short.MAX_VALUE)
                    .add(layout.createSequentialGroup()
                        .add(jLabel1)
                        .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                        .add(jTextFieldFind, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 242, Short.MAX_VALUE))
                    .add(jLabel3)
                    .add(jLabelHits, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 297, Short.MAX_VALUE))
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
                    .add(layout.createSequentialGroup()
                        .add(jLabel2)
                        .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                        .add(jLabelSelection, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 282, Short.MAX_VALUE))
                    .add(layout.createSequentialGroup()
                        .add(220, 220, 220)
                        .add(jButtonCancel)
                        .add(18, 18, 18)
                        .add(jButtonAdd, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 78, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE))
                    .add(jScrollPane2, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 402, Short.MAX_VALUE))
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(layout.createSequentialGroup()
                .addContainerGap()
                .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.BASELINE)
                    .add(jLabel1, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 26, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                    .add(jTextFieldFind, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                    .add(jLabel2)
                    .add(jLabelSelection, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 28, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
                    .add(layout.createSequentialGroup()
                        .add(jLabelHits)
                        .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                        .add(jScrollPane1, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 172, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                        .add(jLabel3)
                        .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .add(jScrollPane4, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 112, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE))
                    .add(jScrollPane2, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 340, Short.MAX_VALUE))
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.UNRELATED)
                .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.BASELINE)
                    .add(jButtonAdd)
                    .add(jButtonCancel))
                .addContainerGap())
        );

        pack();
    }// </editor-fold>//GEN-END:initComponents

    @Action
    public void closeAddDialog() {
        if (selectedID != null) {
            selected = true;
        } else {
            selected = false;
        }
        dispose();
    }

    @Action
    public void search() {
        jTableResults.clearSelection();
        resultsDataModel.updateResults();
    }

    @Action
    public void cancel() {
        selected = false;
        dispose();
    }
    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton jButtonAdd;
    private javax.swing.JButton jButtonCancel;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabelHits;
    private javax.swing.JLabel jLabelSelection;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane2;
    private javax.swing.JScrollPane jScrollPane4;
    private javax.swing.JTable jTableResults;
    private javax.swing.JTextArea jTextArea1;
    private javax.swing.JTextField jTextFieldFind;
    private emr.util.XMLTree xMLTree1;
    // End of variables declaration//GEN-END:variables
}
