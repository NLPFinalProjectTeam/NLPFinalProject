
import java.io.*;
import java.util.*;
import java.nio.file.Path;
import java.nio.file.FileSystems;


import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.TextField;
import org.apache.lucene.document.StoredField;
import org.apache.lucene.document.FieldType;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
//import org.apache.lucene.index.IndexWriter.MaxFieldLength;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.store.SimpleFSDirectory;
import org.apache.lucene.util.Version;


public class MyIndexer {

    private String docDirName;
    private String indexDirName;
    private static final int MAXFIELDLEN = 10000;
    
    /**
     * Constructor.
     * @param docDirName The directory of documents
     * @param indexDirName The destination directory of index
     */
    public MyIndexer(String docDirName, String indexDirName) {
        this.docDirName = docDirName;
        this.indexDirName = indexDirName;
    }

    /**
     * Index every document into the destination directory.
     */
    public void buildIndex() throws IOException {

    	Analyzer analyzer = null;
    	Directory directory = null;
    	IndexWriter writer = null;

    	try {

    		analyzer = new StandardAnalyzer();
            Path path = FileSystems.getDefault().getPath(this.indexDirName);
    		directory = new SimpleFSDirectory(path);
    		IndexWriterConfig conf = new IndexWriterConfig(analyzer);
    		writer = new IndexWriter(directory, conf);

    		File[] docfiles = (new File(this.docDirName)).listFiles();

    		for (File docfile : docfiles) {
    			System.out.println("Processing " + docfile.getPath());
    			Document doc = new Document();
    			BufferedReader reader = new BufferedReader(new FileReader(docfile));
                String line = reader.readLine();
    			//doc.add(new Field("body", reader, new FieldType()));
                doc.add(new TextField("body", line, Field.Store.YES));
                doc.add(new StoredField("externalId", docfile.getName()));
    			writer.addDocument(doc);
    		}

    		//writer.optimize();
    		writer.close();

    	} catch (Exception e) {
    		e.printStackTrace();
    	}
    }
    
    /**
     * Main function.
     */
    public static void main(String args[]) throws IOException {
        
        //for (String arg : args) {
          //  System.out.println(arg);
        //}
        MyIndexer indexer = new MyIndexer(args[0], args[1]);
        indexer.buildIndex();
    }

}
