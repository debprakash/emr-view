/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package emr.util;

import au.com.bytecode.opencsv.CSVReader;
import emr.data.EMRNode;
import java.io.File;
import java.io.FileReader;
import java.util.HashSet;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.queryParser.ParseException;
import org.apache.lucene.queryParser.QueryParser;
import org.apache.lucene.search.*;
import org.apache.lucene.store.Directory;
import org.apache.lucene.util.Version;

import java.io.IOException;
import java.io.Reader;
import java.util.Vector;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.LowerCaseFilter;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.ngram.EdgeNGramTokenFilter;
import org.apache.lucene.analysis.ngram.EdgeNGramTokenFilter.Side;
import org.apache.lucene.analysis.standard.StandardTokenizer;
import org.apache.lucene.index.Term;
import org.apache.lucene.store.FSDirectory;

/**
 *
 * @author debprakash
 */
public class SearchIndexBuilder {

    Analyzer analyzer;
    String autoCompleteDir;
    String dir;
    Directory index;
    TopScoreDocCollector collector;
    QueryParser queryparser;
    IndexSearcher searcher;
    int hitsPerPage = 100;
    TermsFilter availableCodesFilter = null;

    public SearchIndexBuilder() throws IOException, ParseException {
        dir = "./resources";
        autoCompleteDir = dir + "/index";
        //analyzer = new StandardAnalyzer(Version.LUCENE_30);
        analyzer = new Analyzer() {
            public TokenStream tokenStream(String fieldName,
                    Reader reader) {
                //System.out.println("fieldName:" + fieldName);
                TokenStream result = new StandardTokenizer(Version.LUCENE_30, reader);
                //result = new StandardFilter(result);
                result = new LowerCaseFilter(result);
                //result = new ASCIIFoldingFilter(result);
                //result = new StopFilter(false, result, StandardAnalyzer.STOP_WORDS_SET);
                result = new EdgeNGramTokenFilter(result, Side.FRONT, 1, 5);
                return result;
            }
        };
    }

    public void openIndex() throws IOException {
        //index = new RAMDirectory();
        index = FSDirectory.open(new File(autoCompleteDir));
        queryparser = new QueryParser(Version.LUCENE_30, "content", analyzer);
        searcher = new IndexSearcher(index, true);
    }

    @Override
    public void finalize() {
        System.out.println("Closing searcher");
        try {
            searcher.close();
        } catch (IOException ex) {
            System.err.println("IOException: " + ex);
            ex.printStackTrace();
        }
    }

    public void buildIndex() throws IOException, ParseException {
        //index = new RAMDirectory();
        index = FSDirectory.open(new File(autoCompleteDir));
        IndexWriter w = new IndexWriter(index, analyzer, true,
                IndexWriter.MaxFieldLength.UNLIMITED);

        String[] termFiles = new String[] {"/DX-codes.csv"};//,"/PX-codes.csv"
        
        for (String s : termFiles) {
            int line_count = 0;
            CSVReader reader = new CSVReader(new FileReader(dir + s));
            String [] nextLine;
            while ((nextLine = reader.readNext()) != null) {
                // nextLine[] is an array of values from the line
                if (nextLine.length != 3) {
                    throw new RuntimeException("Codes file is corrupt at line " + line_count);
                }
                if (line_count > 0) {
                    String id = nextLine[0];
                    if ("202.02".equals(id)) {
                        System.out.println(id + " exists in input");
                    }
                    String name = nextLine[1];
                    String desc = nextLine[2];
                    EMRNode node = new EMRNode(id, name, desc);
                    addDoc(w, node);
                }
                line_count ++;
                //if (line_count > 10) break;
            }
            System.out.println("Read " + line_count + " from " + s);
        }

        w.close();
    }

    private static void addDoc(IndexWriter w, EMRNode node) throws IOException {
        Document doc = new Document();
        doc.add(new Field("id", node.getId(), Field.Store.YES, Field.Index.NOT_ANALYZED));
        doc.add(new Field("name", node.getName(), Field.Store.YES, Field.Index.NOT_ANALYZED));
        doc.add(new Field("desc", node.getDesc(), Field.Store.YES, Field.Index.NOT_ANALYZED));
        doc.add(new Field("content", node.getContent(), Field.Store.NO, Field.Index.ANALYZED));
        w.addDocument(doc);
    }

    public int search(String querystr, Vector<EMRNode> results) throws IOException, ParseException {

        int retval = -1;
        Query q = queryparser.parse(querystr);
        TopDocs docs = null;
        if (availableCodesFilter != null) {
            System.out.println("Searching with terms filter");
            docs = searcher.search(q, availableCodesFilter, hitsPerPage);
        } else {
            docs = searcher.search(q, hitsPerPage);
        }
        if (docs != null) {
            retval = docs.totalHits;
            ScoreDoc[] hits = docs.scoreDocs;
            System.out.println("Found " + retval + " hits for " + querystr);
            for (int i = 0; i < hits.length; ++i) {
                int docId = hits[i].doc;
                Document d = searcher.doc(docId);
                EMRNode node = new EMRNode(d.get("id"), d.get("name"), d.get("desc"));
                if (results != null) {
                    results.add(node);
                } else {
                    System.out.println((i + 1) + ". " + node);
                }
            }
        }
        return retval;
    }

    public static void main(String[] args) throws IOException, ParseException {
        SearchIndexBuilder s = new SearchIndexBuilder();
        s.buildIndex();

        s.openIndex();

        HashSet<String> availableCodes = new HashSet<String>();
        availableCodes.add("202.02");
        availableCodes.add("188.8");
        availableCodes.add("239.4");
        s.createAvailableCodesFilter(availableCodes);

        int top = s.search("202.02", null);
        System.out.println("Top search = " + top);

        top = s.search("188.8", null);
        System.out.println("Top search = " + top);

        top = s.search("239.4", null);
        System.out.println("Top search = " + top);

        top = s.search("487", null);
        System.out.println("Top search = " + top);

        top = s.search("Inf", null);
        System.out.println("Top search = " + top);
    }

    public void createAvailableCodesFilter(HashSet<String> availableCodes) {
        Term t = new Term("id");
        if (availableCodes.size() > 0) {
            availableCodesFilter = new TermsFilter();
            for(String code : availableCodes) {
                if ("202.02".equals(code)) System.out.println("202.02 exits");
                availableCodesFilter.addTerm(t.createTerm(code));
                //availableCodesFilter.addTerm(new Term("id", code));
            }
        }
    }
}
