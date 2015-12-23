/*

 *  Copyright 2011 patnaik.

 */

/*
 * PartialOrder.java
 *
 * Created on Jan 27, 2011, 6:41:22 PM
 */
package emr.partialorder;

import emrvisualization.util.VisualUtils;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.logging.Level;
import java.util.logging.Logger;
import pqtree.PQNode;
import pqtree.PQTree;
import prefuse.data.Graph;
import prefuse.data.Node;

/**
 *
 * @author patnaik
 */
public class PartialOrder {


    private static class Tuple<T> {
        public Tuple(T s, int l, int u) {
            this.s = s;
            this.l = l;
            this.u = u;
        }
        public T s;
        public int l;
        public int u;
    }

    private static boolean test_order(HashMap<Interval, ArrayList<Integer>> pos_map, 
            Interval node_ivl,
            ArrayList<Interval> child_ivls,
            ArrayList<Integer> ref) {

        ArrayList<Integer> node_loc = pos_map.get(node_ivl);
        int i = 0;
        boolean flag = true;
        
        ArrayList<Integer> tst = new ArrayList<Integer>();
        for (Interval ivl : child_ivls) {
            ref.add(pos_map.get(ivl).get(i) - node_loc.get(i));
        }
        //System.out.println("ref:" + ref);
        for (i = 1; i < node_loc.size(); i++) {
            tst.clear();
            for (Interval ivl : child_ivls) {
                tst.add(pos_map.get(ivl).get(i) - node_loc.get(i));
            }
            //System.out.println("tst:" + tst);
            if (!ref.equals(tst)) {
                flag = false;
                break;
            }
        }
        //System.out.println("flag: " + flag);
        return flag;
    }

    static class DummyNode {
        String name = null;
        int type = 0;
        Node internal_node = null;

        private void set(String field, int value) {
            if ("type".equals(field)) this.type = value;
        }

        private void set(String field, String value) {
            if ("name".equals(field)) this.name = value;
        }

        private Node createNode(Graph g) {
            if (internal_node == null) {
                internal_node = g.addNode();
                internal_node.set("name", name);
                internal_node.set("type", type);
            }
            return internal_node;
        }
    }

    static class DummyGraph {
        HashMap<DummyNode, ArrayList<DummyNode>> parents =
                new HashMap<DummyNode, ArrayList<DummyNode>>();
        HashMap<DummyNode, ArrayList<DummyNode>> children =
                new HashMap<DummyNode, ArrayList<DummyNode>>();

        private DummyNode addNode() {
            DummyNode node = new DummyNode();
            parents.put(node, new ArrayList<DummyNode>());
            children.put(node, new ArrayList<DummyNode>());
            return node;
        }

        private void addEdge(DummyNode parent, DummyNode node) {
            parents.get(node).add(parent);
            children.get(parent).add(node);
        }

        public void updateGraph(Graph g, NodePair<DummyNode> ends) {
            LinkedList<DummyNode> queue = new LinkedList<DummyNode>();

            queue.add(ends.getStart());
            while(!queue.isEmpty()) {
                DummyNode node = queue.pop();
                for (DummyNode parent : parents.get(node)) {
                    g.addEdge(parent.createNode(g), node.createNode(g));
                }
                for (DummyNode child : children.get(node)) {
                    queue.add(child);
                }
            }
        }
    }

    private static Tuple<NodePair<DummyNode>> updateGraph_BFS(PQNode node,
            String[] ref_list,
            DummyGraph g,
            HashMap<Interval, ArrayList<Integer>> pos_map) {

        ArrayList<NodePair<DummyNode>> vect = new ArrayList<NodePair<DummyNode>>();
        if (node.hasChildren()) {
            try {

                int l_min = ref_list.length; int u_max = 0;
                ArrayList<Interval> child_ivls = new ArrayList<Interval>();
                for (Object child : node.getAllChildren()) {
                    Tuple<NodePair<DummyNode>> t = updateGraph_BFS((PQNode) child, ref_list, g, pos_map);
                    child_ivls.add(new Interval(t.l,t.u));
                    l_min = Math.min(l_min, t.l);
                    u_max = Math.max(u_max, t.u);
                    vect.add(t.s);
                }
                Interval node_ivl = new Interval(l_min, u_max);
                ArrayList<Integer> indices = new ArrayList<Integer>();
                boolean flag = test_order(pos_map, node_ivl, child_ivls, indices);

                // Format the children
                NodePair<DummyNode> s_new = null;
                if (flag) {
                    //Serial Order
                    DummyNode last_node = null;
                    DummyNode start_node = null;
                    for (int i : normalize(indices)) {
                        NodePair<DummyNode> np = vect.get(i);
                        if (last_node != null) {
                            g.addEdge(last_node, np.getStart());
                        } else {
                            start_node = np.getStart();
                        }
                        last_node = np.getEnd();
                    }
                    s_new = new NodePair<DummyNode>(start_node, last_node);
                } else {
                    // Parallel Order
                    DummyNode s0 = g.addNode(); s0.set("type", 1);
                    DummyNode e0 = g.addNode(); e0.set("type", 1);
                    for (NodePair<DummyNode> np : vect) {
                        g.addEdge(s0, np.getStart());
                        g.addEdge(np.getEnd(), e0);
                    }
                    s_new = new NodePair(s0, e0);
                }
                return new Tuple<NodePair<DummyNode>>(s_new, l_min, u_max);
            } catch (Exception ex) {
                Logger.getLogger(PartialOrder.class.getName()).log(Level.SEVERE, null, ex);
            }
        } else {
            int l = (Integer)node.getData();
            DummyNode new_node = g.addNode();
            new_node.set("name", ref_list[l]);
            new_node.set("type", 0);
            return new Tuple<NodePair<DummyNode>>(new NodePair<DummyNode>(new_node, new_node), l, l);
        }
        return null;
    }





    private static Tuple<NodePair<Node>> updateGraph(PQNode node,
            String[] ref_list,
            Graph g,
            HashMap<Interval, ArrayList<Integer>> pos_map) {

        ArrayList<NodePair<Node>> vect = new ArrayList<NodePair<Node>>();
        if (node.hasChildren()) {
            try {

                int l_min = ref_list.length; int u_max = 0;
                ArrayList<Interval> child_ivls = new ArrayList<Interval>();
                for (Object child : node.getAllChildren()) {
                    Tuple<NodePair<Node>> t = updateGraph((PQNode) child, ref_list, g, pos_map);
                    child_ivls.add(new Interval(t.l,t.u));
                    l_min = Math.min(l_min, t.l);
                    u_max = Math.max(u_max, t.u);
                    vect.add(t.s);
                }
                Interval node_ivl = new Interval(l_min, u_max);
                ArrayList<Integer> indices = new ArrayList<Integer>();
                boolean flag = test_order(pos_map, node_ivl, child_ivls, indices);

                // Format the children
                NodePair<Node> s_new = null;
                if (flag) {
                    //Serial Order
                    Node last_node = null;
                    Node start_node = null;
                    for (int i : normalize(indices)) {
                        NodePair<Node> np = vect.get(i);
                        if (last_node != null) {
                            g.addEdge(last_node, np.getStart());
                        } else {
                            start_node = np.getStart();
                        }
                        last_node = np.getEnd();
                    }
                    s_new = new NodePair<Node>(start_node, last_node);
                } else {
                    // Parallel Order
                    Node s0 = g.addNode(); s0.set("type", 1);
                    Node e0 = g.addNode(); e0.set("type", 1);
                    for (NodePair<Node> np : vect) {
                        g.addEdge(s0, np.getStart());
                        g.addEdge(np.getEnd(), e0);
                    }
                    s_new = new NodePair(s0, e0);
                }
                return new Tuple<NodePair<Node>>(s_new, l_min, u_max);
            } catch (Exception ex) {
                Logger.getLogger(PartialOrder.class.getName()).log(Level.SEVERE, null, ex);
            }
        } else {
            int l = (Integer)node.getData();
            Node new_node = g.addNode();
            new_node.set("name", ref_list[l]);
            new_node.set("type", 0);
            return new Tuple<NodePair<Node>>(new NodePair<Node>(new_node, new_node), l, l);
        }
        return null;
    }


    public static Tuple<String> str_node(PQNode node,
            String[] ref_list,
            HashMap<Interval, ArrayList<Integer>> pos_map) throws Exception {

        ArrayList<String> vect = new ArrayList<String>();
        if (node.hasChildren()) {

            int l_min = ref_list.length; int u_max = 0;
            ArrayList<Interval> child_ivls = new ArrayList<Interval>();
            for (Object child : node.getAllChildren()) {
                Tuple<String> t = str_node((PQNode)child, ref_list, pos_map);
                child_ivls.add(new Interval(t.l,t.u));
                l_min = Math.min(l_min, t.l);
                u_max = Math.max(u_max, t.u);
                vect.add(t.s);
            }
            Interval node_ivl = new Interval(l_min, u_max);
            ArrayList<Integer> indices = new ArrayList<Integer>();
            boolean flag = test_order(pos_map, node_ivl, child_ivls, indices);

            // Format the children
            String s_new = "";
            if (flag) {
                s_new =  "(" + VisualUtils.join(vect, "->", normalize(indices)) + ")";
            } else {
                Collections.sort(vect);
                s_new =  "(" + VisualUtils.join(vect, " ") + ")";
            }

            //System.out.println(s_new);
            return new Tuple<String>(s_new, l_min, u_max);
        } else {
            int l = (Integer)node.getData();
            return new Tuple<String>(ref_list[l], l, l);
        }
    }




    public static ArrayList<Integer> normalize(ArrayList<Integer> ref){

        ArrayList<Integer> idx = new ArrayList<Integer>(ref);
        Collections.sort(idx);

        HashMap<Integer, Integer> idx_map = new HashMap<Integer, Integer>();
        for(int i = 0; i < idx.size(); i++) idx_map.put(idx.get(i), i);

        ArrayList<Integer> ret_list = new ArrayList<Integer>();
        for (int x : ref) ret_list.add(idx_map.get(x));

        return ret_list;
    }




    public static String generate_partial_order(ArrayList<String[]> sequences, int count) {
        if (sequences.size() == 1) {
            return "(" + VisualUtils.join(sequences.get(0), "->") + ")";
        }
        int n = sequences.get(0).length;
        HashMap<Interval, ArrayList<Integer>> pos_map =
                new HashMap<Interval, ArrayList<Integer>>();
        ArrayList<Interval> C = CommonIntervals.common_intervals(sequences, pos_map, count);

        try {
            PQTree T = new PQTree(n);
            for (Interval s : C) {
                T.reduction(s.getLeft(), s.getRight());
            }
            return str_node(T.getRoot(), sequences.get(0), pos_map).s;
        } catch (Exception ex) {
            Logger.getLogger(PartialOrder.class.getName()).log(Level.SEVERE, null, ex);
        }
        return null;
    }

    public static Graph graphPartialOrder(ArrayList<String[]> sequences) {

        Graph g = new Graph(true);
        g.addColumn("name", String.class);
        g.addColumn("type", Integer.class);

        if (sequences.size() == 1) {
            Node last_node = g.addNode();
            last_node.set("type", 1);
            for (String name : sequences.get(0)) {
                Node new_node = g.addNode();
                new_node.set("name", name);
                new_node.set("type", 0);
                if (last_node != null) {
                    g.addEdge(last_node, new_node);
                }
                last_node = new_node;
            }
            Node new_node = g.addNode();
            new_node.set("type", 1);
            g.addEdge(last_node, new_node);
        } else if (sequences.size() > 1){
            int n = sequences.get(0).length;
            HashMap<Interval, ArrayList<Integer>> pos_map =
                    new HashMap<Interval, ArrayList<Integer>>();
            ArrayList<Interval> C = CommonIntervals.common_intervals(sequences, pos_map);

            try {
                PQTree T = new PQTree(n);
                for (Interval s : C) {
                    T.reduction(s.getLeft(), s.getRight());
                }
                
                //updateGraph(T.getRoot(), sequences.get(0), g, pos_map);
                DummyGraph dummy_g = new DummyGraph();
                NodePair<DummyNode> ends = updateGraph_BFS(T.getRoot(),
                        sequences.get(0), dummy_g, pos_map).s;
                dummy_g.updateGraph(g, ends);


            } catch (Exception ex) {
                Logger.getLogger(PartialOrder.class.getName()).log(Level.SEVERE, null, ex);
            }
        } else {
            return null;
        }
        return g;
    }
}
