/*

 *  Copyright 2011 patnaik.

 */

/*
 * SearchPanel.java
 *
 * Created on Jan 24, 2011, 7:40:18 PM
 */
package emrvisualization;

import emr.data.EMRNode;
import emr.partialorder.PartialOrder;
import emr.util.XMLTree;
import emrvisualization.util.VisualUtils;
import java.awt.Component;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Enumeration;
import java.util.HashSet;
import java.util.List;
import java.util.prefs.Preferences;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import javax.swing.AbstractListModel;
import javax.swing.ComboBoxModel;
import javax.swing.JDialog;
import javax.swing.JFileChooser;
import javax.swing.JOptionPane;
import javax.swing.JTable;
import javax.swing.JTextArea;
import javax.swing.ListModel;
import javax.swing.ListSelectionModel;
import javax.swing.ProgressMonitorInputStream;
import javax.swing.SwingConstants;
import javax.swing.UIManager;
import javax.swing.border.EmptyBorder;
import javax.swing.event.ListDataEvent;
import javax.swing.event.ListDataListener;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import javax.swing.table.AbstractTableModel;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableModel;
import prefuse.data.Graph;

/**
 *
 * @author patnaik
 */
public class SearchPanel extends javax.swing.JFrame {

    private AddNodeJDialog addDialog;
    private JDialog aboutBox;
    private FilterListModel includeListModel, excludeListModel;
    private PatternTableModel resultsTableModel;//, selectionTableModel;
    private SerialEpisodeTableModel serialepisodeTableModel;
    private ArrayList<Pair> results = new ArrayList<Pair>();
    private HashSet<String> availableCodes = new HashSet<String>();
    private JFileChooser jc;
    private SelectionListener listener;
    private SerialSelectionListener seriallistener;
    ArrayList<String> sizes = new ArrayList<String>();
    int limit = 1000;
    private String fileDesc = "";
    private boolean has_significance = false;

    /** Creates new form SearchPanel */
    public SearchPanel() {
        initComponents();
        XMLTree.makeRootNode();
        XMLTree.updateLookUp();

        //VisualUtils.setColumnSizes(jTableSelection, new double[]{0.1, 0.9});

        listener = new SelectionListener(jTableResults);
        jTableResults.getSelectionModel().addListSelectionListener(listener);

        seriallistener = new SerialSelectionListener(jTableSerialEpisodes);
        jTableSerialEpisodes.getSelectionModel().addListSelectionListener(seriallistener);

        jListCodesInclude.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        jListCodesExclude.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);

        VisualUtils.setColumnSizes(jTableSerialEpisodes, new double[]{0.2, 0.6, 0.2});
        VisualUtils.setColumnSizes(jTableDesc, new double[]{0.2, 0.8});

        jTableDesc.getColumnModel().getColumn(0).setCellRenderer(new MultiLineCellRenderer());
        jTableDesc.getColumnModel().getColumn(1).setCellRenderer(new MultiLineCellRenderer());
        jTableDesc.setRowHeight(35);

        this.addWindowListener(new WindowAdapter() {

            @Override
            public void windowClosing(WindowEvent e) {
                closeApplication();
            }
        });
    }

    private void closeApplication() {
        int result = JOptionPane.showConfirmDialog(this, "Are you sure you want to quit?",
                "Quit", JOptionPane.YES_NO_OPTION);
        if (result == JOptionPane.YES_OPTION) {
            System.exit(0);
        }
    }


    class MultiLineCellRenderer extends JTextArea implements TableCellRenderer {

        public MultiLineCellRenderer() {
            setLineWrap(true);
            setWrapStyleWord(true);
            setOpaque(true);
            setRows(2);
        }

        public Component getTableCellRendererComponent(JTable table, Object value,
                boolean isSelected, boolean hasFocus, int row, int column) {
            if (isSelected) {
                setForeground(table.getSelectionForeground());
                setBackground(table.getSelectionBackground());
            } else {
                setForeground(table.getForeground());
                setBackground(table.getBackground());
            }
            setFont(table.getFont());
            if (hasFocus) {
                setBorder(UIManager.getBorder("Table.focusCellHighlightBorder"));
                if (table.isCellEditable(row, column)) {
                    setForeground(UIManager.getColor("Table.focusCellForeground"));
                    setBackground(UIManager.getColor("Table.focusCellBackground"));
                }
            } else {
                setBorder(new EmptyBorder(1, 2, 1, 2));
            }
            if (value != null) {
                setText(value.toString());
                setToolTipText(value.toString());
            } else {
                setText("");
                setToolTipText("");
            }
            return this;
        }
    }

    public EMRNode showAddDialog() {
        if (addDialog == null) {
            addDialog = new AddNodeJDialog(this);
        }
        addDialog.setAvailableCodes(availableCodes);
        addDialog.setLocationRelativeTo(this);
        addDialog.setVisible(true);

        if (addDialog.isSelected()) {
            return addDialog.getSelectedID();
        }
        return null;
    }

    public void showAboutBox() {
        if (aboutBox == null) {
            aboutBox = new EMRVisualizationAboutBox(this);
            aboutBox.setLocationRelativeTo(this);
        }
        aboutBox.setVisible(true);
    }

    private void browseResultFile() {
        Preferences prefs = Preferences.userRoot().node("EMRVisualization");
        if (jc == null) {
            prefs.get("INPUT_FOLDER_PATH", System.getProperty("user.dir"));
            jc = new JFileChooser(prefs.get("INPUT_FOLDER_PATH", System.getProperty("user.dir")));
        }
        if (jc.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
            final File inputfile = jc.getSelectedFile();
            prefs.put("INPUT_FOLDER_PATH", jc.getCurrentDirectory().getAbsolutePath());
            System.out.println("Loading: " + inputfile);
            

            new Thread(new Runnable() {

                public void run() {
                    if (loadResults(inputfile)) {
                        java.awt.EventQueue.invokeLater(new Runnable() {

                            public void run() {
                                jTextFieldInputFile.setText(inputfile.getAbsolutePath());
                                jLabelDesc.setText("Description: " + fileDesc);
                                resultsTableModel = new PatternTableModel(results);
                                jTableResults.setModel(resultsTableModel);

                                if (has_significance) {
                                    VisualUtils.setColumnSizes(jTableResults,
                                            new double[]{0.1, 0.35, 0.35, 0.1, 0.1});
                                } else {
                                    VisualUtils.setColumnSizes(jTableResults,
                                            new double[]{0.1, 0.4, 0.4, 0.1});
                                }
                                jTableResults.updateUI();
                            }
                        });
                    }
                }
            }).start();
        }
    }

    private void refineSearch() {

        jTableResults.clearSelection();
        jTableSerialEpisodes.clearSelection();
        jLabelSerialEpisodeDetails.setText("");
        jLabelSerialEpisodeDetails.setToolTipText("");
        jTableDesc.clearSelection();

        listener.prevIndex = -1;
        seriallistener.prevIndex = -1;

        int sizeFilterType = 0, episode_size = 0;
        String sizeFilterText = (String) jComboEpisodeSize.getSelectedItem();
        sizeFilterText = sizeFilterText.trim();
        if (sizeFilterText.equalsIgnoreCase("ANY")) {
            sizeFilterType = 0;
        } else if (sizeFilterText.startsWith(">")) {
            sizeFilterType = 1;
            try {
                episode_size = Integer.parseInt(sizeFilterText.substring(1));
            } catch (NumberFormatException nfe) {
                JOptionPane.showMessageDialog(this, "Please enter 'ANY' or integer "
                        + "e.g, 3, <3, >3\n for episode size filter", "Error in episode size",
                        JOptionPane.ERROR_MESSAGE);
                return;
            }
        } else if (sizeFilterText.startsWith("<")) {
            sizeFilterType = 2;
            try {
                episode_size = Integer.parseInt(sizeFilterText.substring(1));
            } catch (NumberFormatException nfe) {
                JOptionPane.showMessageDialog(this, "Please enter 'ANY' or integer "
                        + "e.g, 3, <3, >3\n for episode size filter", "Error in episode size",
                        JOptionPane.ERROR_MESSAGE);
                return;
            }
        } else {
            sizeFilterType = 3;
            try {
                episode_size = Integer.parseInt(sizeFilterText);
            } catch (NumberFormatException nfe) {
                JOptionPane.showMessageDialog(this, "Please enter 'ANY' or integer "
                        + "e.g, 3, <3, >3\n for episode size filter", "Error in episode size",
                        JOptionPane.ERROR_MESSAGE);
                return;
            }
        }

        if (!sizes.contains(sizeFilterText)) {
            sizes.add(0, sizeFilterText);
        }
        jComboEpisodeSize.updateUI();

        boolean hasMore = false;
        ArrayList<Integer> indexList = new ArrayList<Integer>();

        ArrayList<String> includeCodes = new ArrayList<String>();
        ArrayList<String> includePositions = new ArrayList<String>();
        for (EMRNode2 node : ((FilterListModel) jListCodesInclude.getModel()).nodelist) {
            includeCodes.add(node.getId().trim());
            includePositions.add(node.position);
        }
        ArrayList<String> excludeCodes = new ArrayList<String>();
        for (EMRNode node : ((FilterListModel) jListCodesExclude.getModel()).nodelist) {
            excludeCodes.add(node.getId().trim());
        }

        for (int i = 0; i < results.size(); i++) {
            Pair p = results.get(i);
            List<String> episode = Arrays.asList(p.episode);

            boolean sizeFlag = true;
            switch (sizeFilterType) {
                case 0: //ANY
                    sizeFlag = true;
                    break;
                case 1:// >3
                    if (p.episode.length <= episode_size) {
                        sizeFlag = false;
                    }
                    break;
                case 2:// <3
                    if (p.episode.length >= episode_size) {
                        sizeFlag = false;
                    }
                    break;
                case 3:// =3
                    if (p.episode.length != episode_size) {
                        sizeFlag = false;
                    }
                    break;
            }



            if (!sizeFlag) {
                continue;
            }

            //Process Includes
            boolean includeFlag = true;

            if (!includeCodes.isEmpty()) {
                if (jRadioButtonAndInclude.isSelected()) {
                    includeFlag = true;
                } else {
                    includeFlag = false;
                }
                int idx = 0;
                for (String s : includeCodes) {
                    boolean flag;
                    String position = includePositions.get(idx);
                    if ("^".equals(position)) {
                        flag = false;
                        for (String[] serial_episode : p.serial_list) {
                            flag = flag || s.equalsIgnoreCase(serial_episode[0]);
                            if (flag) {
                                break;
                            }
                        }
                    } else if ("$".equals(position)) {
                        flag = false;
                        for (String[] serial_episode : p.serial_list) {
                            flag = flag || s.equalsIgnoreCase(serial_episode[serial_episode.length - 1]);
                            if (flag) {
                                break;
                            }
                        }
                    } else {
                        flag = episode.contains(s);
                    }

                    if (jRadioButtonAndInclude.isSelected()) {
                        includeFlag = includeFlag && flag;
                    } else {
                        includeFlag = includeFlag || flag;
                    }
                    idx++;
                }
            }

            if (!includeFlag) {
                continue;
            }

            //Process Excludes
            boolean excludeFlag = false;

            if (!excludeCodes.isEmpty()) {
                if (jRadioButtonAndExclude.isSelected()) {
                    excludeFlag = true;
                    for (String s : excludeCodes) {
                        excludeFlag = excludeFlag && episode.contains(s);
                    }
                } else {
                    excludeFlag = false;
                    for (String s : excludeCodes) {
                        excludeFlag = excludeFlag || episode.contains(s);
                    }
                }
            }

            if (excludeFlag) {
                continue;
            }

            //Add index to index list
            if (indexList.size() < limit) {
                indexList.add(i);
            } else {
                hasMore = true;
                break;
            }

        }
        ((PatternTableModel) jTableResults.getModel()).setIndexList(indexList, hasMore);
        jTableResults.clearSelection();
        jTableResults.updateUI();
        clearEpisodeSelection();
        System.out.println("Search results refine. Hits = " + indexList.size());
        if (hasMore) {
            System.out.println("*There are more results.");
        }

    }

    class Pair implements Comparable {

        String[] episode;
        int serial;
        int count;
        ArrayList<String[]> serial_list;
        ArrayList<String[]> mean_vect;
        ArrayList<String[]> sd_vect;
        ArrayList<Integer> counts;
        ArrayList<Boolean> selections;
        String partialOrder = null;
        private double significance = 0.0;

        public Pair(String[] episode, int serial, int count) {
            this.episode = episode;
            this.serial = serial;
            this.count = count;
            this.serial_list = new ArrayList<String[]>();
            this.mean_vect = new ArrayList<String[]>();
            this.sd_vect = new ArrayList<String[]>();
            this.counts = new ArrayList<Integer>();
            this.selections = new ArrayList<Boolean>();
        }

        public void addSerialEpisode(String[] serial_episode, int count, boolean select, String[] ivl_mean, String[] ivl_sd) {
            serial_list.add(serial_episode);
            counts.add(count);
            selections.add(select);
            if (ivl_mean != null) {
                mean_vect.add(ivl_mean);
            }
            if (ivl_sd != null) {
                sd_vect.add(ivl_sd);
            }
        }

        public void generatePartialOrder() {
            if (serial_list.size() > 0) {
                int i = 0;
                while(i <selections.size() && selections.get(i)) i++;
                this.partialOrder = PartialOrder.generate_partial_order(serial_list, i);
            }
        }

        public int compareTo(Object o) {
            if (o instanceof Pair) {
                Pair other = (Pair) o;
                if (episode.length < other.episode.length) {
                    return -1;
                } else if (episode.length > other.episode.length) {
                    return 1;
                } else {
                    for (int i = 0; i < episode.length && i < other.episode.length; i++) {
                        int val = episode[i].compareTo(other.episode[i]);
                        if (val != 0) {
                            return val;
                        }
                    }
                    return 0;
                }
            }
            return -1;
        }

        private void setSignificance(double significance) {
            this.significance = significance;
        }
    }


    private String readInputStream(BufferedReader in)
            throws IOException, NumberFormatException {

        int p_count = 0;
        String line = null;
        StringBuilder desc = new StringBuilder();
        while ((line = in.readLine()) != null) {
            if (line.startsWith("#")) {
                desc.append(line.substring(1));
                desc.append(" ");
            } else {
                String[] parts = line.split(",");
                int index = Integer.parseInt(parts[0]);
                int len = Integer.parseInt(parts[1]);
                int count = Integer.parseInt(parts[2]);
                double significance = 0;
                if (parts.length > 3) {
                    has_significance = true;
                    significance = Double.parseDouble(parts[5]);
                } else {
                    has_significance = false;
                }
                line = in.readLine();
                String[] episode = line.split("\\|");
                for (String code : episode) {
                    availableCodes.add(code);
                }
                Pair newpair = new Pair(episode, index, count);
                if (has_significance) newpair.setSignificance(significance);
                int sum_count = 0;
                for (int i = 0; i < len && (line = in.readLine()) != null; i++) {
                    parts = line.split(":");
                    int serial_count = Integer.parseInt(parts[1]);
                    boolean select = Integer.parseInt(parts[2]) == 1;
                    String[] serial_episode = parts[0].split("\\|");
                    String[] ivl_mean = null;
                    String[] ivl_sd = null;
                    if (parts.length > 3) {
                        ivl_mean = parts[3].split("\\|");
                        ivl_sd = parts[4].split("\\|");
                    }
                    newpair.addSerialEpisode(serial_episode, serial_count, select, ivl_mean, ivl_sd);
                    sum_count += serial_count;
                }
                if (sum_count != count) {
                    System.err.println(VisualUtils.join(episode, ",") +
                            " : unequal counts " + count + " != " + sum_count);
                }
                newpair.generatePartialOrder();
                resultsTableModel.add(newpair);
                p_count++;
            }
        }
        in.close();
        System.out.println("Has significance " + has_significance);
        System.out.println("Total number of episodes loaded = " + p_count);
        return desc.toString();
    }

    
    private boolean loadResults(File selectedFile) {
        if (selectedFile.exists()) {
            String new_desc = null;
            availableCodes.clear();
            resultsTableModel.clear();
            try {
                BufferedReader in = null;
                if (selectedFile.getName().toUpperCase().endsWith(".ZIP")) {
                    ZipFile zip = new ZipFile(selectedFile);
                    Enumeration znum = zip.entries();

                    while (znum.hasMoreElements()) {
                        ZipEntry entry = (ZipEntry) znum.nextElement();
                        InputStream zis = zip.getInputStream(entry);
                        System.out.println("Reading zip file entry:" + entry);
                        in = new BufferedReader(new InputStreamReader(new ProgressMonitorInputStream(this, "Reading episodes file", zis)));
                        String desc = readInputStream(in);
                        if (new_desc == null) new_desc = desc;
                    }
                } else {
                    System.out.println("Reading file:" + selectedFile.getName());
                    in = new BufferedReader(new InputStreamReader(new ProgressMonitorInputStream(this, "Reading episodes file", new FileInputStream(selectedFile))));
                    new_desc = readInputStream(in);
                }

            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Error occured : " + ex.getClass().getName(),
                        "Loading episodes", JOptionPane.ERROR_MESSAGE);
                ex.printStackTrace();
                return false;
            }
            if (new_desc != null) fileDesc = new_desc;
            else fileDesc = "";
        }
        return true;
    }
    DescriptionTableModel descriptionTableModel;

    private TableModel getDescriptionTableModel() {
        if (descriptionTableModel == null) {
            descriptionTableModel = new DescriptionTableModel();
        }
        return descriptionTableModel;
    }

    private void processEpisodeSelection(int index) {
        jTableSerialEpisodes.clearSelection();
        seriallistener.prevIndex = -1;
        jLabelSerialEpisodeDetails.setText("");
        jLabelSerialEpisodeDetails.setToolTipText("");
        jTableDesc.clearSelection();

        Pair p = resultsTableModel.get(index);
        serialepisodeTableModel.setInternalData(p);
        jTableSerialEpisodes.updateUI();
        //String porder = PartialOrder.generate_partial_order(p.serial_list);

        ArrayList<EMRNode> pattern_desc = new ArrayList<EMRNode>();
        for (String code : p.episode) {
            EMRNode node = XMLTree.getNode(code);
            if (node != null) {
                pattern_desc.add(node);
            }
        }
        //buf.append("Partial Order: " + porder + "\n");
        descriptionTableModel.update(pattern_desc);
        jTableDesc.updateUI();
        generatePartialOrder();
    }

    private void clearEpisodeSelection() {
        listener.prevIndex = -1;
        seriallistener.prevIndex = -1;

        serialepisodeTableModel.setInternalData(null);
        jTableSerialEpisodes.updateUI();
        descriptionTableModel.update(null);
        jTableDesc.updateUI();
        prefusePanel1.clearGraph();

    }

    private void processSerialEpisodeSelection(int index, Pair episode_pair) {
        String labelTxt = "-";
        if (episode_pair != null) {
            StringBuilder txt = new StringBuilder();
            String[] serial_episode = episode_pair.serial_list.get(index);
            String[] means = null, sds = null;
            if (episode_pair.mean_vect != null && 
                    episode_pair.sd_vect != null &&
                    episode_pair.mean_vect.size() > 0 &&
                    episode_pair.sd_vect.size() > 0) {
                means = episode_pair.mean_vect.get(index);
                sds = episode_pair.sd_vect.get(index);
            }
            for (int i = 0; i < serial_episode.length; i++) {
                if (i > 0) {
                    if (means != null && sds != null) {
                        txt.append("=(");
                        txt.append(means[i - 1]);
                        txt.append(",");
                        txt.append(sds[i - 1]);
                        txt.append(")=>");
                    } else {
                        txt.append("=>");
                    }
                }
                txt.append(serial_episode[i]);
            }
            labelTxt = txt.toString();
        }
        jLabelSerialEpisodeDetails.setText(labelTxt);
        jLabelSerialEpisodeDetails.setToolTipText(labelTxt);
    }

    public void generatePartialOrder() {
        Pair p = serialepisodeTableModel.getInternalData();

        ArrayList<String[]> sequences = new ArrayList<String[]>();
        for (int i = 0; i < p.serial_list.size(); i++) {
            if (p.selections.get(i)) {
                sequences.add(p.serial_list.get(i));
            }
        }
        Graph g = PartialOrder.graphPartialOrder(sequences);
        prefusePanel1.addGraph(g);
    }

    ListModel getIncludeListModel() {
        if (includeListModel == null) {
            includeListModel = new FilterListModel();
        }
        return includeListModel;
    }

    ListModel getExcludeListModel() {
        if (excludeListModel == null) {
            excludeListModel = new FilterListModel();
        }
        return excludeListModel;
    }

    TableModel getResultsTableModel() {
        if (resultsTableModel == null) {
            resultsTableModel = new PatternTableModel(results);
        }
        return resultsTableModel;
    }

    TableModel getSerialepisodeTableModel() {
        if (serialepisodeTableModel == null) {
            serialepisodeTableModel = new SerialEpisodeTableModel();
        }
        return serialepisodeTableModel;
    }

    class EpisodeSizeListModel implements ComboBoxModel {

        String selectedItem = "ANY";
        ArrayList<ListDataListener> listeners = new ArrayList<ListDataListener>();

        public EpisodeSizeListModel() {
            sizes.add("ANY");
            sizes.add("2");
            sizes.add("3");
            sizes.add(">3");
        }

        public int getSize() {
            return sizes.size();
        }

        public Object getElementAt(int index) {
            return sizes.get(index);
        }

        public void setSelectedItem(Object anItem) {
            for (ListDataListener l : listeners) {
                l.contentsChanged(new ListDataEvent(jComboEpisodeSize,
                        ListDataEvent.CONTENTS_CHANGED, 0, sizes.size() - 1));
            }
            this.selectedItem = anItem.toString();
        }

        public Object getSelectedItem() {
            return selectedItem;
        }

        public void addListDataListener(ListDataListener l) {
            listeners.add(l);
        }

        public void removeListDataListener(ListDataListener l) {
            listeners.remove(l);
        }
    }

    class EMRNode2 extends EMRNode {

        String position = "";

        public EMRNode2(EMRNode node, String position) {
            super(node.getId(), node.getName(), node.getDesc());
            if ("^Begin".equals(position)) {
                this.position = "^";
            }
            if ("$End".equals(position)) {
                this.position = "$";
            }
        }

        @Override
        public String toString() {
            return this.position + super.toString();
        }
    }

    class FilterListModel extends AbstractListModel {

        ArrayList<EMRNode2> nodelist = new ArrayList<EMRNode2>();

        public int getSize() {
            return nodelist.size();
        }

        public Object getElementAt(int i) {
            return nodelist.get(i);
        }

        public void addNode(EMRNode node, String position) {
            nodelist.add(new EMRNode2(node, position));
        }

        public void removeNode(int index) {
            if (index >= 0 && index < nodelist.size()) {
                nodelist.remove(index);
            }
        }
    }


    class PatternTableModel extends AbstractTableModel {

        ArrayList<Pair> pairlist;
        ArrayList<Integer> indexList;
        boolean hasMore = false;

        public PatternTableModel(ArrayList<Pair> pairlist) {
            this.pairlist = pairlist;
            indexList = new ArrayList<Integer>();
            if (this.pairlist.size() > limit) {
                hasMore = true;
            }
            for (int i = 0; i < this.pairlist.size() && i < limit; i++) {
                indexList.add(i);
            }
        }

        public void setIndexList(ArrayList<Integer> indexList, boolean hasMore) {
            this.indexList = indexList;
            this.hasMore = hasMore;
        }

        public int getRowCount() {
            if (indexList == null) {
                return 0;
            }
            if (indexList.size() < limit) {
                return indexList.size();
            } else if (hasMore) {
                return limit + 1;
            } else {
                return limit;
            }
        }

        public int getColumnCount() {
            int retval = 4;
            if (has_significance) retval = 5;
            return retval;
        }

        public Object getValueAt(int row, int col) {
            if (row >= 0 && row <= indexList.size()) {
                switch (col) {
                    case 0:
                        return pairlist.get(row).serial;
                    case 1:
                        if (row == limit && hasMore) {
                            return "<more>";
                        }
                        return VisualUtils.join(pairlist.get(indexList.get(row)).episode, ", ");
                    case 2:
                        if (row == limit && hasMore) {
                            return "<more>";
                        }
                        return pairlist.get(indexList.get(row)).partialOrder;
                    case 3:
                        return pairlist.get(row).count;
                    case 4:
                        return pairlist.get(row).significance;
                }
            }
            return "";
        }

        @Override
        public String getColumnName(int i) {
            switch (i) {
                case 0:
                    return "Serial";
                case 1:
                    return "Codes";
                case 2:
                    return "Partial Order";
                case 3:
                    return "Count";
                case 4:
                    return "Score";
            }
            return null;
        }

        @Override
        public Class<?> getColumnClass(int i) {
            switch (i) {
                case 0:
                    return Integer.class;
                case 1:
                    return String.class;
                case 2:
                    return String.class;
                case 3:
                    return Integer.class;
                case 4:
                    return Double.class;
            }
            return null;
        }

        public Pair get(int index) {
            return pairlist.get(indexList.get(index));
        }

        private void add(Pair p) {
            pairlist.add(p);
            int index = pairlist.size() - 1;
            if (index < limit) {
                indexList.add(index);
            } else {
                hasMore = true;
            }
        }

        private void clear() {
            pairlist.clear();
            indexList.clear();
            hasMore = false;
        }
    }

    class SerialEpisodeTableModel extends AbstractTableModel {

        private Pair episode_pair;

        public void setInternalData(Pair p) {
            this.episode_pair = p;
        }

        public Pair getInternalData() {
            return this.episode_pair;
        }

        public int getRowCount() {
            if (episode_pair != null) {
                return episode_pair.serial_list.size();
            }
            return 0;
        }

        public int getColumnCount() {
            return 3;
        }

        public Object getValueAt(int row, int col) {
            switch (col) {
                case 0:
                    return episode_pair.selections.get(row);
                case 1:
                    return VisualUtils.join(episode_pair.serial_list.get(row), "  >  ");
                case 2:
                    return episode_pair.counts.get(row);
            }
            return null;
        }

        @Override
        public String getColumnName(int i) {
            switch (i) {
                case 0:
                    return "Select";
                case 1:
                    return "Pattern";
                case 2:
                    return "Count";
            }
            return null;
        }

        @Override
        public Class<?> getColumnClass(int i) {
            switch (i) {
                case 0:
                    return Boolean.class;
                case 1:
                    return String.class;
                case 2:
                    return Integer.class;
            }
            return null;
        }

        @Override
        public boolean isCellEditable(int row, int col) {
            if (col == 0) {
                return true;
            }
            return false;
        }

        @Override
        public void setValueAt(Object aValue, int row, int col) {
            boolean value = (Boolean) aValue;
            if (col == 0) {
                episode_pair.selections.set(row, value);
                generatePartialOrder();
            }
        }
    }

    public class DescriptionTableModel extends AbstractTableModel {

        ArrayList<EMRNode> emr_list = null;

        public int getRowCount() {
            if (emr_list == null) {
                return 0;
            }
            return emr_list.size();
        }

        public int getColumnCount() {
            return 2;
        }

        public Object getValueAt(int row, int col) {
            if (emr_list == null) {
                return null;
            }
            EMRNode node = emr_list.get(row);
            switch (col) {
                case 0:
                    return node.getId();
                case 1:
                    return node.getName() + ":" + node.getDesc();
            }
            return null;
        }

        public void update(ArrayList<EMRNode> emr_list) {
            this.emr_list = emr_list;
        }

        @Override
        public String getColumnName(int col) {
            switch (col) {
                case 0:
                    return "Code";
                case 1:
                    return "Desc";
            }
            return null;
        }
    }

    public class SelectionListener
            implements ListSelectionListener {

        JTable table;
        int prevIndex = -1;

        // It is necessary to keep the table since it is not possible
        // to determine the table from the event's source
        SelectionListener(JTable table) {
            this.table = table;
        }

        public void valueChanged(ListSelectionEvent e) {
            // If cell selection is enabled, both row and column change events are fired
            if (e.getSource() == table.getSelectionModel()
                    && table.getRowSelectionAllowed() && table.getSelectedRowCount() == 1) {
                // Column selection changed
                int index = table.getSelectedRow();
                if (index != prevIndex) {
                    processEpisodeSelection(index);
                }
                prevIndex = index;
            }
        }
    }

    public class SerialSelectionListener
            implements ListSelectionListener {

        JTable table;
        int prevIndex = -1;

        // It is necessary to keep the table since it is not possible
        // to determine the table from the event's source
        SerialSelectionListener(JTable table) {
            this.table = table;
        }

        public void valueChanged(ListSelectionEvent e) {
            // If cell selection is enabled, both row and column change events are fired
            if (e.getSource() == table.getSelectionModel()
                    && table.getRowSelectionAllowed() && table.getSelectedRowCount() == 1) {
                // Column selection changed
                int index = table.getSelectedRow();
                if (index != prevIndex) {
                    processSerialEpisodeSelection(index, serialepisodeTableModel.episode_pair);
                }
                prevIndex = index;
            }
        }
    }

    /**
     * @param args the command line arguments
     */
    public static void main(String args[]) {

        System.out.println("Current directory : " + System.getProperty("user.dir"));
        System.out.println("Please make sure the current directory has the folder: 'resources'");

        java.awt.EventQueue.invokeLater(new Runnable() {

            public void run() {
                new SearchPanel().setVisible(true);
            }
        });
    }

    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        buttonGroup1 = new javax.swing.ButtonGroup();
        buttonGroup2 = new javax.swing.ButtonGroup();
        jRadioButton1 = new javax.swing.JRadioButton();
        jPanel1 = new javax.swing.JPanel();
        jPanel8 = new javax.swing.JPanel();
        jPanel4 = new javax.swing.JPanel();
        jComboEpisodeSize = new javax.swing.JComboBox();
        jPanel5 = new javax.swing.JPanel();
        jScrollPane4 = new javax.swing.JScrollPane();
        jListCodesInclude = new javax.swing.JList();
        jRadioButtonAndInclude = new javax.swing.JRadioButton();
        jRadioButtonOrInclude = new javax.swing.JRadioButton();
        jButtonAddIncludes = new javax.swing.JButton();
        jButtonRemoveInclude = new javax.swing.JButton();
        jPanel7 = new javax.swing.JPanel();
        jButtonRefineSearch = new javax.swing.JButton();
        jPanel6 = new javax.swing.JPanel();
        jScrollPane5 = new javax.swing.JScrollPane();
        jListCodesExclude = new javax.swing.JList();
        jRadioButtonAndExclude = new javax.swing.JRadioButton();
        jRadioButtonOrExclude = new javax.swing.JRadioButton();
        jButtonAddExclude = new javax.swing.JButton();
        jButtonRemoveExclude = new javax.swing.JButton();
        jPanel9 = new javax.swing.JPanel();
        jLabel1 = new javax.swing.JLabel();
        jTextFieldInputFile = new javax.swing.JTextField();
        jButtonBrowse = new javax.swing.JButton();
        jLabelDesc = new javax.swing.JLabel();
        jPanel2 = new javax.swing.JPanel();
        jScrollPane1 = new javax.swing.JScrollPane();
        jTableResults = new javax.swing.JTable();
        jPanel3 = new javax.swing.JPanel();
        prefusePanel1 = new emrvisualization.PrefusePanel();
        jLabel2 = new javax.swing.JLabel();
        jScrollPane3 = new javax.swing.JScrollPane();
        jTableSerialEpisodes = new javax.swing.JTable();
        jLabel3 = new javax.swing.JLabel();
        jScrollPane6 = new javax.swing.JScrollPane();
        jTableDesc = new javax.swing.JTable();
        jLabelSerialEpisodeDetails = new javax.swing.JTextField();
        jLabel4 = new javax.swing.JLabel();
        jMenuBar1 = new javax.swing.JMenuBar();
        jMenu2 = new javax.swing.JMenu();
        jMenuItemAbout = new javax.swing.JMenuItem();
        jSeparator1 = new javax.swing.JPopupMenu.Separator();
        jMenuItemExit = new javax.swing.JMenuItem();

        jRadioButton1.setText("jRadioButton1");

        setDefaultCloseOperation(javax.swing.WindowConstants.DO_NOTHING_ON_CLOSE);

        jPanel8.setBorder(javax.swing.BorderFactory.createTitledBorder("Filter criteria"));

        jPanel4.setBorder(javax.swing.BorderFactory.createTitledBorder("Episode Size"));

        jComboEpisodeSize.setEditable(true);
        jComboEpisodeSize.setModel(new EpisodeSizeListModel());

        org.jdesktop.layout.GroupLayout jPanel4Layout = new org.jdesktop.layout.GroupLayout(jPanel4);
        jPanel4.setLayout(jPanel4Layout);
        jPanel4Layout.setHorizontalGroup(
            jPanel4Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jComboEpisodeSize, 0, 166, Short.MAX_VALUE)
        );
        jPanel4Layout.setVerticalGroup(
            jPanel4Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jPanel4Layout.createSequentialGroup()
                .add(jComboEpisodeSize, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(66, Short.MAX_VALUE))
        );

        jPanel5.setBorder(javax.swing.BorderFactory.createTitledBorder("Include"));

        jListCodesInclude.setModel(getIncludeListModel());
        jScrollPane4.setViewportView(jListCodesInclude);

        buttonGroup1.add(jRadioButtonAndInclude);
        jRadioButtonAndInclude.setSelected(true);
        jRadioButtonAndInclude.setText("And");

        buttonGroup1.add(jRadioButtonOrInclude);
        jRadioButtonOrInclude.setText("Or");

        jButtonAddIncludes.setText("Add");
        jButtonAddIncludes.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButtonAddIncludesActionPerformed(evt);
            }
        });

        jButtonRemoveInclude.setText("Remove");
        jButtonRemoveInclude.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButtonRemoveIncludeActionPerformed(evt);
            }
        });

        org.jdesktop.layout.GroupLayout jPanel5Layout = new org.jdesktop.layout.GroupLayout(jPanel5);
        jPanel5.setLayout(jPanel5Layout);
        jPanel5Layout.setHorizontalGroup(
            jPanel5Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jPanel5Layout.createSequentialGroup()
                .add(jScrollPane4, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 114, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(jPanel5Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
                    .add(jButtonRemoveInclude)
                    .add(jButtonAddIncludes)
                    .add(jPanel5Layout.createSequentialGroup()
                        .add(jRadioButtonAndInclude)
                        .addPreferredGap(org.jdesktop.layout.LayoutStyle.UNRELATED)
                        .add(jRadioButtonOrInclude))))
        );

        jPanel5Layout.linkSize(new java.awt.Component[] {jButtonAddIncludes, jButtonRemoveInclude}, org.jdesktop.layout.GroupLayout.HORIZONTAL);

        jPanel5Layout.setVerticalGroup(
            jPanel5Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jPanel5Layout.createSequentialGroup()
                .add(jPanel5Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.BASELINE)
                    .add(jRadioButtonAndInclude)
                    .add(jRadioButtonOrInclude))
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(jButtonAddIncludes)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.UNRELATED)
                .add(jButtonRemoveInclude))
            .add(jScrollPane4, 0, 0, Short.MAX_VALUE)
        );

        jButtonRefineSearch.setText("Refine Search");
        jButtonRefineSearch.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButtonRefineSearchActionPerformed(evt);
            }
        });

        org.jdesktop.layout.GroupLayout jPanel7Layout = new org.jdesktop.layout.GroupLayout(jPanel7);
        jPanel7.setLayout(jPanel7Layout);
        jPanel7Layout.setHorizontalGroup(
            jPanel7Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(org.jdesktop.layout.GroupLayout.TRAILING, jPanel7Layout.createSequentialGroup()
                .addContainerGap(99, Short.MAX_VALUE)
                .add(jButtonRefineSearch)
                .addContainerGap())
        );
        jPanel7Layout.setVerticalGroup(
            jPanel7Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jPanel7Layout.createSequentialGroup()
                .addContainerGap()
                .add(jButtonRefineSearch)
                .addContainerGap(76, Short.MAX_VALUE))
        );

        jPanel6.setBorder(javax.swing.BorderFactory.createTitledBorder("Exclude"));

        jListCodesExclude.setModel(getExcludeListModel());
        jScrollPane5.setViewportView(jListCodesExclude);

        buttonGroup2.add(jRadioButtonAndExclude);
        jRadioButtonAndExclude.setText("And");

        buttonGroup2.add(jRadioButtonOrExclude);
        jRadioButtonOrExclude.setSelected(true);
        jRadioButtonOrExclude.setText("Or");

        jButtonAddExclude.setText("Add");
        jButtonAddExclude.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButtonAddExcludeActionPerformed(evt);
            }
        });

        jButtonRemoveExclude.setText("Remove");
        jButtonRemoveExclude.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButtonRemoveExcludeActionPerformed(evt);
            }
        });

        org.jdesktop.layout.GroupLayout jPanel6Layout = new org.jdesktop.layout.GroupLayout(jPanel6);
        jPanel6.setLayout(jPanel6Layout);
        jPanel6Layout.setHorizontalGroup(
            jPanel6Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jPanel6Layout.createSequentialGroup()
                .add(jScrollPane5, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 114, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(jPanel6Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
                    .add(jButtonRemoveExclude)
                    .add(jButtonAddExclude)
                    .add(jPanel6Layout.createSequentialGroup()
                        .add(jRadioButtonAndExclude)
                        .addPreferredGap(org.jdesktop.layout.LayoutStyle.UNRELATED)
                        .add(jRadioButtonOrExclude))))
        );

        jPanel6Layout.linkSize(new java.awt.Component[] {jButtonAddExclude, jButtonRemoveExclude}, org.jdesktop.layout.GroupLayout.HORIZONTAL);

        jPanel6Layout.setVerticalGroup(
            jPanel6Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jPanel6Layout.createSequentialGroup()
                .add(jPanel6Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.BASELINE)
                    .add(jRadioButtonAndExclude)
                    .add(jRadioButtonOrExclude))
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(jButtonAddExclude)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.UNRELATED)
                .add(jButtonRemoveExclude))
            .add(jScrollPane5, 0, 0, Short.MAX_VALUE)
        );

        org.jdesktop.layout.GroupLayout jPanel8Layout = new org.jdesktop.layout.GroupLayout(jPanel8);
        jPanel8.setLayout(jPanel8Layout);
        jPanel8Layout.setHorizontalGroup(
            jPanel8Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jPanel8Layout.createSequentialGroup()
                .add(jPanel5, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(jPanel6, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(jPanel4, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(jPanel7, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );
        jPanel8Layout.setVerticalGroup(
            jPanel8Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jPanel7, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
            .add(jPanel4, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
            .add(jPanel5, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
            .add(jPanel6, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
        );

        jPanel9.setBorder(javax.swing.BorderFactory.createTitledBorder("Patterns loader"));

        jLabel1.setText("File:");

        jTextFieldInputFile.setEditable(false);
        jTextFieldInputFile.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jTextFieldInputFileActionPerformed(evt);
            }
        });

        jButtonBrowse.setText("Browse");
        jButtonBrowse.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButtonBrowseActionPerformed(evt);
            }
        });

        jLabelDesc.setHorizontalAlignment(SwingConstants.LEFT);
        jLabelDesc.setText("Description:");
        jLabelDesc.setVerticalAlignment(SwingConstants.TOP);

        org.jdesktop.layout.GroupLayout jPanel9Layout = new org.jdesktop.layout.GroupLayout(jPanel9);
        jPanel9.setLayout(jPanel9Layout);
        jPanel9Layout.setHorizontalGroup(
            jPanel9Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jPanel9Layout.createSequentialGroup()
                .add(jLabel1)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(jTextFieldInputFile, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 781, Short.MAX_VALUE)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(jButtonBrowse, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 88, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE))
            .add(jLabelDesc, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 914, Short.MAX_VALUE)
        );
        jPanel9Layout.setVerticalGroup(
            jPanel9Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jPanel9Layout.createSequentialGroup()
                .add(jPanel9Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.BASELINE)
                    .add(jLabel1)
                    .add(jTextFieldInputFile, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                    .add(jButtonBrowse))
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(jLabelDesc, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        org.jdesktop.layout.GroupLayout jPanel1Layout = new org.jdesktop.layout.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(org.jdesktop.layout.GroupLayout.TRAILING, jPanel8, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
            .add(org.jdesktop.layout.GroupLayout.TRAILING, jPanel9, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jPanel1Layout.createSequentialGroup()
                .add(jPanel9, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .add(9, 9, 9)
                .add(jPanel8, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        jPanel2.setBorder(javax.swing.BorderFactory.createTitledBorder("List of patterns:"));

        jTableResults.setModel(getResultsTableModel());
        jTableResults.setGridColor(new java.awt.Color(204, 204, 204));
        jScrollPane1.setViewportView(jTableResults);

        jPanel3.setBorder(javax.swing.BorderFactory.createTitledBorder("Pattern Display:"));

        jLabel2.setText("Sequences:");

        jTableSerialEpisodes.setModel(getSerialepisodeTableModel());
        jTableSerialEpisodes.setGridColor(new java.awt.Color(204, 204, 204));
        jScrollPane3.setViewportView(jTableSerialEpisodes);

        jLabel3.setText("Partial Order:");

        jTableDesc.setModel(getDescriptionTableModel());
        jTableDesc.setGridColor(new java.awt.Color(204, 204, 204));
        jScrollPane6.setViewportView(jTableDesc);

        jLabelSerialEpisodeDetails.setEditable(false);
        jLabelSerialEpisodeDetails.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jLabelSerialEpisodeDetailsActionPerformed(evt);
            }
        });

        jLabel4.setText("Details:");

        org.jdesktop.layout.GroupLayout jPanel3Layout = new org.jdesktop.layout.GroupLayout(jPanel3);
        jPanel3.setLayout(jPanel3Layout);
        jPanel3Layout.setHorizontalGroup(
            jPanel3Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(org.jdesktop.layout.GroupLayout.TRAILING, jPanel3Layout.createSequentialGroup()
                .add(jPanel3Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
                    .add(jLabel2)
                    .add(jScrollPane3, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 432, Short.MAX_VALUE)
                    .add(jScrollPane6, 0, 0, Short.MAX_VALUE)
                    .add(jPanel3Layout.createSequentialGroup()
                        .add(jLabel4)
                        .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                        .add(jLabelSerialEpisodeDetails, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 374, Short.MAX_VALUE)))
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(jPanel3Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
                    .add(jPanel3Layout.createSequentialGroup()
                        .add(jLabel3)
                        .addContainerGap())
                    .add(prefusePanel1, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 460, Short.MAX_VALUE)))
        );
        jPanel3Layout.setVerticalGroup(
            jPanel3Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jPanel3Layout.createSequentialGroup()
                .add(jPanel3Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.BASELINE)
                    .add(jLabel2)
                    .add(jLabel3))
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(jPanel3Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
                    .add(jPanel3Layout.createSequentialGroup()
                        .add(jScrollPane3, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 67, Short.MAX_VALUE)
                        .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                        .add(jPanel3Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.BASELINE)
                            .add(jLabelSerialEpisodeDetails, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                            .add(jLabel4))
                        .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                        .add(jScrollPane6, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 74, Short.MAX_VALUE))
                    .add(prefusePanel1, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 185, Short.MAX_VALUE)))
        );

        org.jdesktop.layout.GroupLayout jPanel2Layout = new org.jdesktop.layout.GroupLayout(jPanel2);
        jPanel2.setLayout(jPanel2Layout);
        jPanel2Layout.setHorizontalGroup(
            jPanel2Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jScrollPane1, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 914, Short.MAX_VALUE)
            .add(jPanel3, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
        );
        jPanel2Layout.setVerticalGroup(
            jPanel2Layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jPanel2Layout.createSequentialGroup()
                .add(jScrollPane1, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 136, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(jPanel3, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        jMenu2.setText("Help");

        jMenuItemAbout.setAccelerator(javax.swing.KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_A, java.awt.event.InputEvent.ALT_MASK));
        jMenuItemAbout.setText("About");
        jMenuItemAbout.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jMenuItemAboutActionPerformed(evt);
            }
        });
        jMenu2.add(jMenuItemAbout);
        jMenu2.add(jSeparator1);

        jMenuItemExit.setAccelerator(javax.swing.KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_X, java.awt.event.InputEvent.ALT_MASK));
        jMenuItemExit.setText("Exit");
        jMenuItemExit.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jMenuItemExitActionPerformed(evt);
            }
        });
        jMenu2.add(jMenuItemExit);

        jMenuBar1.add(jMenu2);

        setJMenuBar(jMenuBar1);

        org.jdesktop.layout.GroupLayout layout = new org.jdesktop.layout.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jPanel1, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
            .add(jPanel2, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(layout.createSequentialGroup()
                .add(jPanel1, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(jPanel2, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        pack();
    }// </editor-fold>//GEN-END:initComponents

    private void jTextFieldInputFileActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jTextFieldInputFileActionPerformed
        // TODO add your handling code here:
    }//GEN-LAST:event_jTextFieldInputFileActionPerformed

    private void jButtonAddIncludesActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButtonAddIncludesActionPerformed
        EMRNode code = showAddDialog();
        if (code != null) {
            System.out.println("Code selected = " + code);
            String[] locations = new String[]{"^Begin", "Anywhere", "$End"};
            String position = (String) JOptionPane.showInputDialog(this,
                    "Require " + code.getId() + " at:",
                    "Position of code", JOptionPane.QUESTION_MESSAGE, null, locations, locations[1]);
            if (position != null) {
                includeListModel.addNode(code, position);
            }
            jListCodesInclude.updateUI();
        }

    }//GEN-LAST:event_jButtonAddIncludesActionPerformed

    private void jMenuItemAboutActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jMenuItemAboutActionPerformed
        showAboutBox();
    }//GEN-LAST:event_jMenuItemAboutActionPerformed

    private void jButtonBrowseActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButtonBrowseActionPerformed
        browseResultFile();
    }//GEN-LAST:event_jButtonBrowseActionPerformed

    private void jButtonAddExcludeActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButtonAddExcludeActionPerformed
        EMRNode code = showAddDialog();
        if (code != null) {
            excludeListModel.addNode(code, "");
            jListCodesExclude.updateUI();
        }
    }//GEN-LAST:event_jButtonAddExcludeActionPerformed

    private void jButtonRemoveIncludeActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButtonRemoveIncludeActionPerformed
        int selectedIndex = jListCodesInclude.getSelectedIndex();
        if (selectedIndex != -1) {
            includeListModel.removeNode(selectedIndex);
            jListCodesInclude.updateUI();
        }
    }//GEN-LAST:event_jButtonRemoveIncludeActionPerformed

    private void jButtonRemoveExcludeActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButtonRemoveExcludeActionPerformed
        int selectedIndex = jListCodesExclude.getSelectedIndex();
        if (selectedIndex != -1) {
            excludeListModel.removeNode(selectedIndex);
            jListCodesExclude.updateUI();
        }
    }//GEN-LAST:event_jButtonRemoveExcludeActionPerformed

    private void jButtonRefineSearchActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButtonRefineSearchActionPerformed
        refineSearch();
    }//GEN-LAST:event_jButtonRefineSearchActionPerformed

    private void jMenuItemExitActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jMenuItemExitActionPerformed
        closeApplication();
    }//GEN-LAST:event_jMenuItemExitActionPerformed

    private void jLabelSerialEpisodeDetailsActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jLabelSerialEpisodeDetailsActionPerformed
        // TODO add your handling code here:
    }//GEN-LAST:event_jLabelSerialEpisodeDetailsActionPerformed

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.ButtonGroup buttonGroup1;
    private javax.swing.ButtonGroup buttonGroup2;
    private javax.swing.JButton jButtonAddExclude;
    private javax.swing.JButton jButtonAddIncludes;
    private javax.swing.JButton jButtonBrowse;
    private javax.swing.JButton jButtonRefineSearch;
    private javax.swing.JButton jButtonRemoveExclude;
    private javax.swing.JButton jButtonRemoveInclude;
    private javax.swing.JComboBox jComboEpisodeSize;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabelDesc;
    private javax.swing.JTextField jLabelSerialEpisodeDetails;
    private javax.swing.JList jListCodesExclude;
    private javax.swing.JList jListCodesInclude;
    private javax.swing.JMenu jMenu2;
    private javax.swing.JMenuBar jMenuBar1;
    private javax.swing.JMenuItem jMenuItemAbout;
    private javax.swing.JMenuItem jMenuItemExit;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JPanel jPanel2;
    private javax.swing.JPanel jPanel3;
    private javax.swing.JPanel jPanel4;
    private javax.swing.JPanel jPanel5;
    private javax.swing.JPanel jPanel6;
    private javax.swing.JPanel jPanel7;
    private javax.swing.JPanel jPanel8;
    private javax.swing.JPanel jPanel9;
    private javax.swing.JRadioButton jRadioButton1;
    private javax.swing.JRadioButton jRadioButtonAndExclude;
    private javax.swing.JRadioButton jRadioButtonAndInclude;
    private javax.swing.JRadioButton jRadioButtonOrExclude;
    private javax.swing.JRadioButton jRadioButtonOrInclude;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane3;
    private javax.swing.JScrollPane jScrollPane4;
    private javax.swing.JScrollPane jScrollPane5;
    private javax.swing.JScrollPane jScrollPane6;
    private javax.swing.JPopupMenu.Separator jSeparator1;
    private javax.swing.JTable jTableDesc;
    private javax.swing.JTable jTableResults;
    private javax.swing.JTable jTableSerialEpisodes;
    private javax.swing.JTextField jTextFieldInputFile;
    private emrvisualization.PrefusePanel prefusePanel1;
    // End of variables declaration//GEN-END:variables
}
