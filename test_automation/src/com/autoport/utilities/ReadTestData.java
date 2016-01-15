package com.autoport.utilities;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import java.util.Properties;

import com.opencsv.CSVReader;

public class ReadTestData {

	public static String[][] readCSV(String dataFileName) throws IOException {

		String userDir = System.getProperty("user.dir");
		String filepath = userDir + "/test_data/" + dataFileName + ".csv";
		CSVReader csvReader = null;

		try {
			csvReader = new CSVReader(new FileReader(filepath));
			String[] row = null;
			List<String[]> allData = csvReader.readAll();
			int noOfRows = allData.size();
			int noOfColumns = ((String[]) allData.get(0)).length;

			String[][] dataTable = new String[noOfRows - 1][noOfColumns];

			for (int i = 1; i < noOfRows; i++) {
				row = (String[]) allData.get(i);
				for (int j = 0; j < noOfColumns; j++) {
					dataTable[i - 1][j] = row[j];
				}
			}

			return dataTable;

		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			if (csvReader != null) {

				try {
					csvReader.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}
		return null;

	}

	public static String readParameter(String filename, String parameterName) {

		/*
		 * StackTraceElement[] stackTraceElements =
		 * Thread.currentThread().getStackTrace();
		 * 
		 * String dataFileName = stackTraceElements[2].getClassName();
		 */

		/*
		 * String userDir = System.getProperty("user.dir"); String filepath =
		 * userDir + "/test_data/" + filename + ".csv"; CSVReader csvReader =
		 * null;
		 * 
		 * try { csvReader = new CSVReader(new FileReader(filepath)); String[]
		 * row = null; List<String[]> allData = csvReader.readAll(); int
		 * noOfRows = allData.size();
		 * 
		 * for (int i = 0; i < noOfRows; i++) { row = (String[]) allData.get(i);
		 * if (row[0].equalsIgnoreCase(parameterName)) { return row[1]; } } }
		 * catch (FileNotFoundException e) { e.printStackTrace(); } catch
		 * (IOException e) { e.printStackTrace(); } finally { if (csvReader !=
		 * null) {
		 * 
		 * try { csvReader.close(); } catch (IOException e) {
		 * e.printStackTrace(); } } } return null;
		 */

		try {
			Properties prop = new Properties();
			String userDir = System.getProperty("user.dir");
			String filepath = userDir + "/test_data/" + filename + ".properties";

			InputStream is = new FileInputStream(filepath);

			prop.load(is);

			String parameter = prop.getProperty(parameterName);

			return parameter;
		} catch (FileNotFoundException ex) {
			ex.printStackTrace();
		} catch (IOException ex) {
			ex.printStackTrace();
		}

		return null;

	}

	public static void writeParameter(String filename, String key, String parameterName) {

		try {
			Properties prop = new Properties();
			String userDir = System.getProperty("user.dir");
			String filepath = userDir + "/test_data/" + filename + ".properties";

			FileInputStream is = new FileInputStream(filepath);

			prop.load(is);

			FileOutputStream os = new FileOutputStream(filepath);
			prop.setProperty(key, parameterName);
			prop.store(os," ");

			os.close();

		} catch (FileNotFoundException ex) {
			ex.printStackTrace();
		} catch (IOException ex) {
			ex.printStackTrace();
		}

	}
}
