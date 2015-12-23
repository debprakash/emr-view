/*

 *  Copyright 2011 patnaik.

 */

/*
 * CommonIntervals.java
 *
 * Created on Jan 27, 2011, 6:35:43 PM
 */
package emr.partialorder;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;

/**
 *
 * @author patnaik
 */
public class CommonIntervals {

    public static HashSet<Interval> naive_common_interval(int[] pi_AB,
            HashMap<Interval, ArrayList<Integer>> pos_map,
            HashSet<Interval> C_prev) {
        int n = pi_AB.length;
        HashSet<Interval> C = new HashSet<Interval>();
        int l, u;
        for (int x = 0; x < n; x++) {
            l = u = pi_AB[x];
            for (int y = x; y < n; y++) {
                l = Math.min(l, pi_AB[y]);
                u = Math.max(u, pi_AB[y]);
                Interval ivl = new Interval(l, u);
                if (u - l - (y - x) == 0 && (C_prev == null || C_prev.contains(ivl))) {
                    if (!pos_map.containsKey(ivl)) {
                        pos_map.put(ivl, new ArrayList<Integer>());
                    }
                    pos_map.get(ivl).add(x);
                    C.add(ivl);
                }
            }
        }
        return C;
    }





    public static int[] inv_map(String[] seq_1, String[] seq_2) {
        HashMap<String, Integer> m = new HashMap<String, Integer>();
        for (int i = 0; i < seq_1.length; i++) {
            m.put(seq_1[i], i);
        }
        int[] retval = new int[seq_1.length];
        for (int i = 0; i < seq_1.length; i++) {
            retval[i] = m.get(seq_2[i]);
        }
        return retval;
    }


    public static ArrayList<Interval> common_intervals(ArrayList<String[]> sequences,
            HashMap<Interval, ArrayList<Integer>> pos_map) {
        
        int count = sequences.size();
        return common_intervals(sequences, pos_map, count);
    }


    public static ArrayList<Interval> common_intervals(ArrayList<String[]> sequences,
            HashMap<Interval, ArrayList<Integer>> pos_map, int count) {
        HashSet<Interval> C = null;
        ArrayList<Interval> C_list = new ArrayList<Interval>();
        for (int i = 0; i < count; i++) {
            int[] pi_AB = inv_map(sequences.get(0), sequences.get(i));
            C = naive_common_interval(pi_AB, pos_map, C);
        }
        if (C != null) {
            for (Interval ivl : C) {
                C_list.add(ivl);
            }
            Collections.sort(C_list);
        }
        return C_list;
    }
}
