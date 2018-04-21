import java.io.*;
import java.util.*;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.FileSystems;


import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.*;
//import org.apache.lucene.document.Document;
//import org.apache.lucene.document.Field;
//import org.apache.lucene.document.FieldType;
//import org.apache.lucene.DirectoryReader;
import org.apache.lucene.index.*;
import org.apache.lucene.search.*;
//import org.apache.lucene.index.IndexWriter;
//import org.apache.lucene.index.IndexWriter.MaxFieldLength;
//import org.apache.lucene.index.IndexWriterConfig;
//import org.apache.lucene.store.Directory;
import org.apache.lucene.store.*;
//mport org.apache.lucene.store.FSDirectory;
//import org.apache.lucene.store.SimpleFSDirectory;
import org.apache.lucene.util.Version;
import org.apache.lucene.queryparser.classic.QueryParser;


public class MyRetriever {


	private String queryFile;
	private String indexPath;

	public MyRetriever(String queryFile, String indexPath) {

		this.queryFile = queryFile;
		this.indexPath = indexPath;
	}

	public void processQueries() throws Exception {

		BufferedReader reader = new BufferedReader(new FileReader(new File(this.queryFile)));

		String line;
		while ((line = reader.readLine()) != null) {
			this.processQuery(line);
		}
	}

	public void processQuery(String query) throws Exception {

		Analyzer analyzer = new StandardAnalyzer();
		Query q = new QueryParser("body", analyzer).parse(query);

		//System.out.println(q);
		int hitsPerPage = 5;
		IndexReader reader = DirectoryReader.open(FSDirectory.open(Paths.get(this.indexPath)));
		IndexSearcher searcher = new IndexSearcher(reader);
		TopDocs docs = searcher.search(q, hitsPerPage);
		ScoreDoc[] sentences = docs.scoreDocs;

		//System.out.println(reader.document(1).get("body"));
		//System.out.println("searcher.count(q) = " + searcher.count(q));

		//System.out.println("-----------------------");
		System.out.println("Query: " + query);
		//System.out.println(docs.getMaxScore() + "\n");
		//System.out.println(sentences.length);
		//int cnt = 1;
		for (ScoreDoc s : sentences) {
			System.out.println("Score: " + s.score);
			//System.out.println(reader.document(s.doc).get("externalId"));
			System.out.println(searcher.doc(s.doc).get("body"));
			//++cnt;
		}
		//System.out.println("-----------------------\n\n");
		reader.close();

	}


	public static void main(String[] args) throws Exception {
		MyRetriever retriever = new MyRetriever(args[0], args[1]);
		retriever.processQueries();
	}
}
