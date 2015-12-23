/*
 * EMRVisualizationApp.java
 */

package emrvisualization;

import emr.util.XMLTree;
import org.jdesktop.application.Application;
import org.jdesktop.application.SingleFrameApplication;

/**
 * The main class of the application.
 */
public class EMRVisualizationApp extends SingleFrameApplication {

    @Override
    protected void initialize(String[] args) {
        XMLTree.makeRootNode();
    }

    /**
     * At startup create and show the main frame of the application.
     */
    @Override protected void startup() {
        show(new EMRVisualizationView(this));
    }

    /**
     * This method is to initialize the specified window by injecting resources.
     * Windows shown in our application come fully initialized from the GUI
     * builder, so this additional configuration is not needed.
     */
    @Override protected void configureWindow(java.awt.Window root) {
    }

    /**
     * A convenient static getter for the application instance.
     * @return the instance of EMRVisualizationApp
     */
    public static EMRVisualizationApp getApplication() {
        return Application.getInstance(EMRVisualizationApp.class);
    }

    /**
     * Main method launching the application.
     */
    public static void main(String[] args) {
        launch(EMRVisualizationApp.class, args);
    }
}
