package com.autoport.utilities;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.List;

import com.opencsv.CSVReader;

public class ReadTestData {
	
public static String[][] readCSV(String dataFileName) throws IOException{
		
		String userDir = System.getProperty("user.dir");
	    String filepath = userDir + "/test_data/" + dataFileName + ".csv";	    
	    CSVReader csvReader = null;  
		
		try{
			csvReader = new CSVReader(new FileReader(filepath));
			String[] row = null;
			List<String[]> allData = csvReader.readAll();
			int noOfRows = allData.size();
			int noOfColumns = ((String[]) allData.get(0)).length;
			
			String[][] dataTable = new String[noOfRows-1][noOfColumns];
			
			for (int i=1; i<noOfRows ; i++) {		    
				 row = (String[]) allData.get(i);
			     for(int j=0; j<noOfColumns ; j++){
			    	 dataTable[i-1][j] = row[j];
			     }		    
			}			
			
			return dataTable;
			
		}
		catch (FileNotFoundException e) {  
			   e.printStackTrace();  
			  } 
		catch (IOException e) {  
			   e.printStackTrace();  
			  } 
		finally {
				if (csvReader != null) {  
			
			    try {  
			    	csvReader.close();  
			    } 
			    catch (IOException e) {  
			     e.printStackTrace();  
			    }  
		    } 	
		}
		return null;			
		
	}

}
