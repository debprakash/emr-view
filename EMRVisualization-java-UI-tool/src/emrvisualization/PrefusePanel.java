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
 * PrefusePanel.java
 *
 * Created on Dec 26, 2009, 12:37:36 AM
 */
package emrvisualization;

import java.awt.BorderLayout;
import java.awt.geom.Rectangle2D;
import prefuse.Constants;
import prefuse.Display;
import prefuse.Visualization;
import prefuse.action.Action;
import prefuse.action.ActionList;
import prefuse.action.RepaintAction;
import prefuse.action.assignment.ColorAction;
import prefuse.action.assignment.DataColorAction;
import prefuse.action.layout.graph.NodeLinkTreeLayout;
import prefuse.activity.Activity;
import prefuse.controls.DragControl;
import prefuse.controls.PanControl;
import prefuse.controls.ToolTipControl;
import prefuse.controls.ZoomControl;
import prefuse.data.Graph;
import prefuse.data.Node;
import prefuse.render.DefaultRendererFactory;
import prefuse.render.EdgeRenderer;
import prefuse.render.LabelRenderer;
import prefuse.util.ColorLib;
import prefuse.util.GraphicsLib;
import prefuse.util.display.DisplayLib;
import prefuse.visual.VisualItem;

/**
 *
 * @author debprakash
 */
public class PrefusePanel extends javax.swing.JPanel {

    Visualization visual;
    Display display;

    /** Creates new form PrefusePanel */
    public PrefusePanel() {
        initComponents();
        visual = new Visualization();

        display = new Display(visual);
        display.addControlListener(new DragControl());
        display.addControlListener(new PanControl());
        display.addControlListener(new ZoomControl());
        display.addControlListener(new ToolTipControl("desc"));
        display.setHighQuality(true);

        LabelRenderer r = new LabelRenderer("name");
        r.setVerticalPadding(2);
        r.setHorizontalPadding(2);
        //r.setRoundedCorner(2, 2); // round the corners
        EdgeRenderer e = new EdgeRenderer(Constants.EDGE_TYPE_LINE, Constants.EDGE_ARROW_FORWARD);
        e.setArrowHeadSize(5, 5);
        visual.setRendererFactory(new DefaultRendererFactory(r, e));

        ColorAction text = new ColorAction("graph.nodes", VisualItem.TEXTCOLOR, ColorLib.gray(0));
        ColorAction edges = new ColorAction("graph.edges", VisualItem.STROKECOLOR, ColorLib.gray(0));
        ColorAction edgefill = new ColorAction("graph.edges", VisualItem.FILLCOLOR, ColorLib.gray(0));
        //ColorAction fill = new ColorAction("graph.nodes", VisualItem.FILLCOLOR, ColorLib.rgb(180,180,255));
        int[] palette = new int[]{ColorLib.rgb(180, 180, 255), ColorLib.gray(0)};
        DataColorAction fill = new DataColorAction("graph.nodes", "type", Constants.NOMINAL, VisualItem.FILLCOLOR, palette);


        ActionList treelayout = new ActionList();//Activity.INFINITY
        treelayout.add(new NodeLinkTreeLayout("graph"));

        ActionList layout = new ActionList(Activity.INFINITY);
        //layout.add(new ForceDirectedLayout("graph"));
        layout.add(new ZoomCenterAction());
        layout.add(new RepaintAction());

        

        ActionList color = new ActionList();
        color.add(fill);
        color.add(text);
        color.add(edges);
        color.add(edgefill);

        visual.putAction("color", color);
        visual.putAction("layout", layout);
        visual.putAction("tree", treelayout);

        setLayout(new BorderLayout());
        add(display, BorderLayout.CENTER);

    }

    public void addGraph(Graph g) {
        visual.cancel("color");  // assign the colors
        visual.cancel("tree");
        visual.cancel("layout");
        visual.removeGroup("graph");
        if (g != null) {
            visual.addGraph("graph", g);
            visual.run("color");  // assign the colors
            visual.run("tree");
        }
        visual.run("layout"); // start up the animated layout
    }

    public void addDemoGraph() {
        System.out.println("Adding demo graph");
        visual.cancel("color");  // assign the colors
        visual.cancel("tree");
        visual.cancel("layout");

        Graph g = new Graph(true);
        g.addColumn("name", String.class);
        g.addColumn("type", Integer.class);

        Node A = g.addNode();
        A.set("name", "A");
        A.set("type", 0);


        Node B = g.addNode();
        B.set("name", "B");
        B.set("type", 0);

        Node C = g.addNode();
        C.set("name", "C");
        C.set("type", 0);

        Node D = g.addNode();
        D.set("name", "D");
        D.set("type", 0);

        Node s0 = g.addNode();
        s0.set("type", 1);

        Node e0 = g.addNode();
        e0.set("type", 1);

        g.addEdge(A, s0);
        g.addEdge(s0, B);
        g.addEdge(s0, C);
        g.addEdge(B, e0);
        g.addEdge(C, e0);
        g.addEdge(e0, D);

        visual.addGraph("graph", g);

        visual.run("color");  // assign the colors
        visual.run("tree");
        visual.run("layout"); // start up the animated layout
    }

    void clearGraph() {
        visual.cancel("layout");
        visual.cancel("color");  // assign the colors
        visual.removeGroup("graph");
        visual.repaint();
    }

    public class ZoomCenterAction extends Action {
        public void run(double frac) {
            if (display == null || visual == null) return;
            Rectangle2D bounds = visual.getBounds(Visualization.ALL_ITEMS);
            GraphicsLib.expand(bounds, 5 + (int) (1 / display.getScale()));
            DisplayLib.fitViewToBounds(display, bounds, 0);
        }
    }

    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        setName("Form"); // NOI18N

        org.jdesktop.layout.GroupLayout layout = new org.jdesktop.layout.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(0, 400, Short.MAX_VALUE)
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(0, 300, Short.MAX_VALUE)
        );
    }// </editor-fold>//GEN-END:initComponents
    // Variables declaration - do not modify//GEN-BEGIN:variables
    // End of variables declaration//GEN-END:variables
}
