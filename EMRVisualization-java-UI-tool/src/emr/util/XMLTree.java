package emr.util;

import au.com.bytecode.opencsv.CSVReader;
import emr.data.EMRNode;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.*;
import javax.swing.tree.*;
import java.io.*;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Hashtable;
import org.w3c.dom.*;
import javax.xml.parsers.*;
import org.xmlpull.v1.dom2_builder.DOM2XmlPullBuilder;

/** Given a filename or a name and an input stream,
 *  this class generates a JTree representing the
 *  XML structure contained in the file or stream.
 *  Parses with DOM then copies the tree structure
 *  (minus text and comment nodes).
 *
 *  Taken from Core Web Programming from 
 *  Prentice Hall and Sun Microsystems Press,
 *  http://www.corewebprogramming.com/.
 *  &copy; 2001 Marty Hall and Larry Brown;
 *  may be freely used or adapted. 
 */
public class XMLTree extends JTree {

    private static final String dir = "./resources";
    private static final String filename_1 = dir + "/Dtab10.xml";
    private static final String filename_2 = dir + "/Ptab10.xml";
    private static final String filename_new_codes = dir + "/DX-codes.csv";
    private static Hashtable<String, TreePath> pathMap = new Hashtable<String, TreePath>();
    private static DefaultMutableTreeNode rootTreeNode;
    private static final HashMap<String, EMRNode> lookuptable = new HashMap<String, EMRNode>();


    private TreePath prevPath;

    public XMLTree() {
        super(makeRootNode());
    }

    public static void updateLookUp() {
        try {
            CSVReader reader = new CSVReader(new FileReader(filename_new_codes));

            String[] line;
            while((line = reader.readNext()) != null) {
                String id = line[0];
                String name = line[1];
                String desc = line[2];
                EMRNode node = new EMRNode(id, name, desc);
                lookuptable.put(id, node);
            }


            reader.close();
        } catch (IOException ex) {
            Logger.getLogger(XMLTree.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
    

    // This method needs to be static so that it can be called
    // from the call to the parent constructor (super), which
    // occurs before the object is really built.
    public static DefaultMutableTreeNode makeRootNode() {
        if (rootTreeNode == null) {
            try {
                boolean xppflag = true;

                if (xppflag) {

                    DOM2XmlPullBuilder builder = new DOM2XmlPullBuilder();
                    Reader reader = new FileReader(new File(filename_1));
                    Element rootElement = builder.parse(reader);
                    rootTreeNode = buildTree(rootElement);
                    reader.close();

                    reader = new FileReader(new File(filename_2));
                    rootElement = builder.parse(reader);
                    addToTree(rootElement);
                    reader.close();

                } else {

                    DocumentBuilderFactory builderFactory = DocumentBuilderFactory.newInstance();
                    DocumentBuilder builder = builderFactory.newDocumentBuilder();

                    InputStream in = new FileInputStream(new File(filename_1));
                    Document document = builder.parse(in);
                    document.getDocumentElement().normalize();
                    Element rootElement = document.getDocumentElement();
                    rootTreeNode = buildTree(rootElement);
                    in.close();

                    in = new FileInputStream(new File(filename_2));
                    document = builder.parse(in);
                    document.getDocumentElement().normalize();
                    rootElement = document.getDocumentElement();
                    addToTree(rootElement);
                    in.close();
                }

            } catch (Exception e) {
                String errorMessage =
                        "Error making root node: " + e;
                System.err.println(errorMessage);
                e.printStackTrace();
                return (new DefaultMutableTreeNode(errorMessage));
            }
        }
        return (rootTreeNode);
    }

    private static DefaultMutableTreeNode buildTree(Element rootElement) {
        // Make a JTree node for the root, then make JTree
        // nodes for each child and add them to the root node.
        // The addChildren method is recursive.
        rootTreeNode = new DefaultMutableTreeNode(treeNodeLabel(rootElement));
        addChildren(rootTreeNode, rootElement);
        return (rootTreeNode);
    }

    private static void addToTree(Element rootElement) {
        // Make a JTree node for the root, then make JTree
        // nodes for each child and add them to the root node.
        // The addChildren method is recursive.
        addChildren(rootTreeNode, rootElement);
    }

    private static void addChildren(DefaultMutableTreeNode parentTreeNode,
            Node parentXMLElement) {
        // Recursive method that finds all the child elements
        // and adds them to the parent node. We have two types
        // of nodes here: the ones corresponding to the actual
        // XML structure and the entries of the graphical JTree.
        // The convention is that nodes corresponding to the
        // graphical JTree will have the word "tree" in the
        // variable name. Thus, "childElement" is the child XML
        // element whereas "childTreeNode" is the JTree element.
        // This method just copies the non-text and non-comment
        // nodes from the XML structure to the JTree structure.

        NodeList childElements =
                parentXMLElement.getChildNodes();
        for (int i = 0; i < childElements.getLength(); i++) {
            Node childElement = childElements.item(i);
            if (!(childElement instanceof Text
                    || childElement instanceof Comment)) {
                EMRNode node = treeNodeLabel(childElement);
                DefaultMutableTreeNode childTreeNode =
                        new DefaultMutableTreeNode(node);
                parentTreeNode.add(childTreeNode);
                if (node.getId().length() > 0) {
                    pathMap.put(node.getId(), new TreePath(childTreeNode.getPath()));
                }
                addChildren(childTreeNode, childElement);
            }
        }
    }

    // If the XML element has no attributes, the JTree node
    // will just have the name of the XML element. If the
    // XML element has attributes, the names and values of the
    // attributes will be listed in parens after the XML
    // element name. For example:
    // XML Element: <blah>
    // JTree Node:  blah
    // XML Element: <blah foo="bar" baz="quux">
    // JTree Node:  blah (foo=bar, baz=quux)
    private static EMRNode treeNodeLabel(Node childElement) {

        NamedNodeMap elementAttributes =
                childElement.getAttributes();
        EMRNode treeNodeLabel = EMRNode.BLANK;
        if (elementAttributes != null
                && elementAttributes.getLength() > 0) {
            String id = elementAttributes.getNamedItem("id").getNodeValue();
            String name = elementAttributes.getNamedItem("name").getNodeValue();
            String desc = elementAttributes.getNamedItem("desc").getNodeValue();
            treeNodeLabel = new EMRNode(id, name, desc);
            lookuptable.put(id, treeNodeLabel);
        }
        return treeNodeLabel;
    }


    public void gotoNode(String id)
    {
        collapsePrevPath();
        TreePath treePath = pathMap.get(id);
        if (id.endsWith("0") && treePath == null) {
            id = id.substring(0, id.length()-1);
            treePath = pathMap.get(id);
        }
        if (id.endsWith(".") && treePath == null) {
            id = id.substring(0, id.length()-1);
            treePath = pathMap.get(id);
        }
        if (treePath != null) {
            setSelectionPath(treePath);
            scrollPathToVisible(treePath);
            fireTreeExpanded(treePath);
            prevPath = treePath;
        } else {
            //expandAll(false);
            //prevPath = null;
        }
    }

    public void collapsePrevPath() {
        if (prevPath != null) {
            collapsePath(prevPath);
            fireTreeCollapsed(prevPath);
        }
    }

// If expand is true, expands all nodes in the tree.
// Otherwise, collapses all nodes in the tree.
    public void expandAll(boolean expand) {
        TreeNode root = (TreeNode) this.getModel().getRoot();

        // Traverse tree from root
        expandAll(new TreePath(root), expand);
    }

    private void expandAll(TreePath parent, boolean expand) {
        // Traverse children
        TreeNode node = (TreeNode) parent.getLastPathComponent();
        if (node.getChildCount() >= 0) {
            for (Enumeration e = node.children(); e.hasMoreElements();) {
                TreeNode n = (TreeNode) e.nextElement();
                TreePath path = parent.pathByAddingChild(n);
                expandAll(path, expand);
            }
        }
        // Expansion or collapse must be done bottom-up
        if (expand) {
            this.expandPath(parent);
        } else {
            this.collapsePath(parent);
        }
    }


    public static EMRNode getNode(String id) {
        return lookuptable.get(id);
    }


}
