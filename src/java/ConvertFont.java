/* Font conversion program. */

import java.util.Arrays;
import java.util.Queue;
import java.util.LinkedList;
import java.util.List;
import java.util.ArrayList;
import java.io.PrintStream;
import java.io.InputStream;
import java.io.FileInputStream;
import java.io.OutputStream;
import java.io.FileOutputStream;
import java.io.FileNotFoundException;
import java.io.IOException;

import com.google.typography.font.sfntly.FontFactory;
import com.google.typography.font.sfntly.Font;
import com.google.typography.font.sfntly.data.WritableFontData;
import com.google.typography.font.tools.conversion.eot.EOTWriter;
import com.google.typography.font.tools.conversion.woff.WoffWriter;

public class ConvertFont {

	private static final String ERROR = "error";
	private static final String FATAL = "fatal";

	@SuppressWarnings("serial")
	private static class Error extends Exception {
		public Error(String msg) {
			super(msg);
		}
	}

	private static void printList(java.util.Collection<String> c) {
		System.out.println('[');
		for(Object o : c) System.out.println(o);
		System.out.println(']');
	}

	private static interface FontConverter {
		public WritableFontData convert(Font font) throws IOException;
		public String extension();
	}

	private static class EOTConverter implements FontConverter {
		private EOTWriter writer = new EOTWriter();
		public WritableFontData convert(Font font) throws IOException {
			return writer.convert(font);
		}
		public String extension() {
			return "eot";
		}
	}

	private static class WOFFConverter implements FontConverter {
		private WoffWriter writer = new WoffWriter();
		public WritableFontData convert(Font font) throws IOException {
			return writer.convert(font);
		}
		public String extension() {
			return "woff";
		}
	}

	private static FontConverter getFontConverter(String extension) {
		extension = extension.toLowerCase();
		if("woff".equals(extension)) return new WOFFConverter();
		else if("eot".equals(extension)) return new EOTConverter();
		else return null;
	}

	public static void main(String[] argv) {

		try {
			Queue<String> args = new LinkedList<String>(Arrays.asList(argv));

			List<String> fileNames = new ArrayList<String>();
			String formatList = null, selectString = null;

			String arg;
			while((arg = args.poll()) != null) {
				if(arg.equals("--")) {
					fileNames.addAll(args);
					break;
				} else if(arg.equals("-h") || arg.equals("--help")) {
					showHelp(System.out);
					System.exit(0);
				} else if(arg.equals("-f") || arg.equals("--format")) {
					formatList = args.poll();
				} else if(arg.equals("-s") || arg.equals("--select")) {
					selectString = args.poll();
				} else {
					fileNames.add(arg);
				}
			}

			final Integer ALL_FONTS = null;
			Integer fontSelection = ALL_FONTS;
			if(selectString != null) fontSelection = Integer.parseInt(selectString) - 1;

			if(fileNames.isEmpty()) throw new Error("at least one input file is required");
			if(formatList == null) throw new Error("at least one output format is required");

			List<FontConverter> fontConverters = new ArrayList<FontConverter>();
			for(String format : Arrays.asList(formatList.split(","))) {
				FontConverter c = getFontConverter(format.toLowerCase());
				if(c == null) {
					throw new Error(
						"output format " + format + " not recognized\n" +
						"    available formats are: woff, eot"
					);
				}
				fontConverters.add(c);
			}

			/* Arguments have been checked. */

			for(String fileName : fileNames) {

				/* Open the input file. */
				InputStream fin = null;
				fin = new FileInputStream(fileName);

				try {
					/* Read the fonts from the input file. */
					FontFactory fontFactory = FontFactory.getInstance();
					Font[] allFonts = fontFactory.loadFonts(fin);

					List<Font> fonts = new ArrayList<Font>();
					if(fontSelection == ALL_FONTS) {
						fonts.addAll(Arrays.asList(allFonts));
					} else if(fontSelection >= 0 && fontSelection < allFonts.length) {
						fonts.add(allFonts[fontSelection]);
					} else {
						throw new Error("selection " + fontSelection + " not found in " + fileName);
					}

					for(FontConverter c : fontConverters) {
						int i = 0;
						for(Font font : fonts) {
							/* Read the font. */
							WritableFontData data = c.convert(font);

							/* Open the output file. */
							String foutName =
								chopSuffix(fileName) +
								(fonts.size() > 1 ? "." + ++i : "") +
								"." + c.extension();
							OutputStream fout = new FileOutputStream(foutName);
							try {
								/* Write the data to the output file. */
								data.copyTo(fout);
							} finally {
								fout.close();
							}
						}
					}
				} finally {
					fin.close();
				}
			}
		} catch(Error e) {
			showHelp(System.err);
			System.err.println("error: " + e.getMessage());
			System.exit(2);
		} catch(Exception e) {
			e.printStackTrace();
			System.exit(1);
		}
	}

	private static void showHelp(PrintStream out) {
		out.print(
			"ConvertFont -f <formats> <font-files> ...\n" +
			"\n" +
			"Convert font files.\n" +
			"\n" +
			"-h | --help    Show this help message.\n" +
			"-f <formats>   A comma-separated list of the output formats to convert each input font to.\n" +
			"               Supported formats are woff and eot.\n" +
			"--             End of options.\n" +
			"<font-files>   The input font files to be converted.\n"
		);
	}

	private static String chopSuffix(String s) {
		int index = s.lastIndexOf('.');
		return index < 0 ? s : s.substring(0, index);
	}
}
