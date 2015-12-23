/*

 *  Copyright 2011 patnaik.

 */

/*
 * NodePair.java
 *
 * Created on Jan 28, 2011, 10:13:30 AM
 */

package emr.partialorder;

/**
 *
 * @author patnaik
 */
public class NodePair<T> {

    public NodePair(T start, T end) {
        this.start = start;
        this.end = end;
    }

    public T getEnd() {
        return end;
    }

    public T getStart() {
        return start;
    }

    private T start;
    private T end;

}
