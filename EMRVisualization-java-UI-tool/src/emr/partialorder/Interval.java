/*

 *  Copyright 2011 patnaik.

 */

/*
 * Interval.java
 *
 * Created on Jan 27, 2011, 10:35:42 PM
 */

package emr.partialorder;

/**
 *
 * @author patnaik
 */
public class Interval implements Comparable{

    public void setLeft(int left) {
        this.left = left;
    }

    public void setRight(int right) {
        this.right = right;
    }

    public int getLeft() {
        return left;
    }

    public int getRight() {
        return right;
    }

    public Interval(int left, int right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public boolean equals(Object obj) {
        if (obj == null) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        final Interval other = (Interval) obj;
        if (this.left != other.left) {
            return false;
        }
        if (this.right != other.right) {
            return false;
        }
        return true;
    }

    @Override
    public int hashCode() {
        int hash = 7;
        hash = 41 * hash + this.left;
        hash = 41 * hash + this.right;
        return hash;
    }


    private int left;
    private int right;

    public int compareTo(Object obj) {
        if (obj == null) {
            return -1;
        }
        if (getClass() != obj.getClass()) {
            return -1;
        }
        final Interval other = (Interval) obj;
        int retval = new Integer(left).compareTo(other.left);
        if (retval == 0) {
            retval = new Integer(right).compareTo(other.right);
        }
        return retval;
    }

}
