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

package emr.data;

import java.util.StringTokenizer;

/**
 *
 * @author debprakash
 */
public class EMRNode {

    private String id;
    private String name;
    private String desc;

    public EMRNode(String id, String name, String desc) {
        this.id = id;
        this.name = toSentenseCase(name);
        //this.name = name;
        this.desc = toSentenseCase(desc);
        //this.desc = desc;
    }

    public static EMRNode BLANK = new EMRNode("", "", "");

    @Override
    public boolean equals(Object obj) {
        if (obj == null) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        final EMRNode other = (EMRNode) obj;
        if ((this.id == null) ? (other.id != null) : !this.id.equals(other.id)) {
            return false;
        }
        return true;
    }

    @Override
    public int hashCode() {
        int hash = 7;
        hash = 29 * hash + (this.id != null ? this.id.hashCode() : 0);
        return hash;
    }

    @Override
    public String toString() {
        if (id != null && id.length()>0)
            return id + " " + name;
        else
            return name;
    }

    public String getContent() {
        return id + " " + name + " " + desc;
    }

    public String getFormattedContent() {
        return id + ": " + name + " - " + desc;
    }

    public String getDesc() {
        return desc;
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    private static String toSentenseCase(String desc) {

        StringBuilder buffer = new StringBuilder();
        StringTokenizer tok = new StringTokenizer(desc, ".:;", true);
        for(;tok.hasMoreTokens();) {
            String sentence = tok.nextToken();
            if (sentence.length() == 1) {
                buffer.append(sentence);
            } else {
                buffer.append(Character.toUpperCase(sentence.charAt(0)));
                buffer.append(sentence.substring(1));
            }
        }

        //System.out.println(buffer.toString());
        return buffer.toString();
    }

}
