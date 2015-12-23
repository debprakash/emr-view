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

package emrvisualization.util;

import java.awt.Dimension;
import java.util.ArrayList;
import javax.swing.JTable;
import javax.swing.table.TableColumn;

/**
 *
 * @author debprakash
 */
public class VisualUtils {

    public static void setColumnSizes(JTable table, double[] percentages)
    {
        Dimension tableDim = table.getPreferredSize();
        tableDim = table.getSize();

        double total = 0;
        for(double t : percentages) total += t;

        table.setAutoResizeMode(JTable.AUTO_RESIZE_ALL_COLUMNS);
        for(int i = 0; i < table.getColumnModel().getColumnCount(); i++)
        {
            TableColumn column = table.getColumnModel().getColumn(i);
            column.setPreferredWidth((int) (tableDim.width * (percentages[i] / total)));
            //column.setMaxWidth((int) (tableDim.width * (percentages[i] / total)));
            //column.setMinWidth((int) (tableDim.width * (percentages[i] / total)));
        }
    }



    public static String join(String[] s, String delimiter) {
        StringBuilder buffer = new StringBuilder();
        for (int i = 0; i < s.length; i++) {
            if (i != 0) buffer.append(delimiter);
            buffer.append(s[i]);
        }
        return buffer.toString();
    }

    public static String join(ArrayList<String> s, String delimiter) {
        StringBuilder buffer = new StringBuilder();
        for (int i = 0; i < s.size(); i++) {
            if (i != 0) buffer.append(delimiter);
            buffer.append(s.get(i));
        }
        return buffer.toString();
    }

    public static String join(ArrayList<String> s, String delimiter, ArrayList<Integer> indices) {
        StringBuilder buffer = new StringBuilder();
        for (int i = 0; i < s.size(); i++) {
            if (i != 0) buffer.append(delimiter);
            buffer.append(s.get(indices.get(i)));
        }
        return buffer.toString();
    }
}
