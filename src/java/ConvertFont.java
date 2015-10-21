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

	@SuppressWarnings("serial")
	private static class Error extends Exception {

		public Error() {
		}

		public Error(String msg) {
			super(msg);
		}
	}

	private static class UsageError extends Error {
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
		if("woff".equals(extension)) {
			return new WOFFConverter();
		} else if("eot".equals(extension)) {
			return new EOTConverter();
		} else {
			return null;
		}
	}

	public static void main(String[] argv) {

		try {
			Queue<String> args = new LinkedList<String>(Arrays.asList(argv));

			String inputFileName = null;
			List<String> outputFileNames = new ArrayList<String>();
			String selectString = null;

			String arg;
			while((arg = args.poll()) != null) {
				if(arg.equals("-i") || arg.equals("--input")) {
					inputFileName = args.poll();
					break;
				} else if(arg.equals("-o") || arg.equals("--output")) {
					String name = args.poll();
					if(name == null) {
						throw new UsageError();
					}
					outputFileNames.add(name);
				} else if(arg.equals("-s") || arg.equals("--select")) {
					selectString = args.poll();
					if(selectString == null) {
						throw new UsageError();
					}
				} else if(arg.equals("-h") || arg.equals("--help")) {
					showHelp(System.out);
					System.exit(0);
				} else if(inputFileName == null) {
					inputFileName = arg;
				} else {
					throw new UsageError();
				}
			}

			if(inputFileName == null) {
				throw new UsageError();
			}
			if(outputFileNames.isEmpty()) {
				throw new UsageError();
			}
			int fontSelection = 0;
			if(selectString != null) {
				fontSelection = Integer.parseInt(selectString) - 1;
				if(fontSelection < 0) {
					throw new Error("invalid selection number");
				}
			}

			/* Arguments have been checked. */

			/* Check the output formats. */
			List<FontConverter> converters = new ArrayList<FontConverter>(outputFileNames.size());
			for(String outputFileName : outputFileNames) {
				/* Choose the output format based on the file extension. */
				String ext = getExtension(outputFileName);
				if(ext == null) {
					throw new Error("output format for " + outputFileName +
						" not recognized");
				}
				FontConverter converter = getFontConverter(ext);
				if(converter == null) {
					throw new Error("output format " + ext + " not recognized");
				}
				converters.add(converter);
			}

			/* Open the input file. */
			InputStream fin = null;
			fin = new FileInputStream(inputFileName);

			try {
				/* Read the fonts from the input file. */
				FontFactory fontFactory = FontFactory.getInstance();
				Font[] allFonts = fontFactory.loadFonts(fin);

				Font inputFont;
				if(fontSelection < allFonts.length) {
					inputFont = allFonts[fontSelection];
				} else {
					throw new Error("selection " + (fontSelection + 1) + " not found in " + inputFileName);
				}

				for(int i = 0, n = outputFileNames.size(); i < n; ++i) {
					/* Convert the font. */
					WritableFontData data = converters.get(i).convert(inputFont);
					/* Open the output file. */
					OutputStream fout = new FileOutputStream(outputFileNames.get(i));
					try {
						/* Write the data to the output file. */
						data.copyTo(fout);
					} finally {
						fout.close();
					}
				}
			} finally {
				fin.close();
			}
		} catch(UsageError e) {
			showHelp(System.err);
			System.exit(1);
		} catch(Error e) {
			System.err.println("error: " + e.getMessage());
			System.exit(1);
		} catch(Exception e) {
			e.printStackTrace();
			System.exit(1);
		}
	}

	private static void showHelp(PrintStream out) {
		out.print(
			"Usage: java ConvertFont <input-file> -o <output-file>\n" +
			"\n" +
			"  Convert a TTF font file to WOFF and/or EOT.\n" +
			"\n" +
			"Arguments:\n" +
			"  [-i --input] <input-file>\n" +
			"                A TTF font file.\n" +
			"\n" +
			"Options:\n" +
			"  -o --output <output-file>\n" +
			"                The name of an output file to convert the input file to.\n" +
			"                The format is determined by the file extension. Possible output\n" +
			"                formats are .woff and .eot. The `-o` flag may be listed\n" +
			"                multiple times to specify multiple output files.\n" +
			"  -s --select <integer>\n" +
			"                When reading a font with multiple font definitions, selects the\n" +
			"                nth font in the file. By default, selects the first font.\n" +
			"  -h --help     This help message.\n"
		);
	}

	private static String getExtension(String s) {
		int index = s.lastIndexOf('.');
		return index < 0 ? null : s.substring(index + 1);
	}
}
