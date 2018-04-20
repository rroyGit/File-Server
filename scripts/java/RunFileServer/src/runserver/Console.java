package runserver;

import java.awt.BorderLayout;
import java.awt.Desktop;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.net.URL;

import javax.swing.Box.Filler;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollBar;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.ScrollPaneConstants;

import runserver.process.ConsoleProcess;

@SuppressWarnings("serial")
public class Console extends JFrame implements ActionListener {
	
	private boolean isMainConsole;
	private ConsoleProcess process;

	private JTextArea textArea;
	private JScrollBar scrollBar;
	
	public Console(String title, ConsoleProcess process) {
		this(title, process, false);
	}

	public Console(String title, ConsoleProcess process, boolean isMainConsole) {
		super(title);
		
		this.process = process;
		this.isMainConsole = isMainConsole;

		super.setSize(600, 400);
		super.setResizable(false);

		this.textArea = new JTextArea();
		this.textArea.setEditable(false);
		this.textArea.setLineWrap(true);
		this.textArea.setWrapStyleWord(true);

		JPanel topPanel = new JPanel();
		topPanel.setLayout(new FlowLayout());
		super.getContentPane().add(topPanel, BorderLayout.NORTH);
		
		JButton browserButton = new JButton("Open Web UI");
		browserButton.addActionListener(this);
		topPanel.add(browserButton);

		JButton clientButton = new JButton("Start Client");
		clientButton.addActionListener(this);
		topPanel.add(clientButton);
		
		//Dimension d = new Dimension(150, 5);
		//Filler box = new Filler(d, d, d);
		//topPanel.add(box);
		
		JButton testsButton = new JButton("Run Tests");
		testsButton.addActionListener(this);
		topPanel.add(testsButton);
		
		JButton restartButton = new JButton("Restart");
		restartButton.addActionListener(this);
		topPanel.add(restartButton);
		
		JButton shutdownButton = new JButton("Shutdown");
		shutdownButton.addActionListener(this);
		topPanel.add(shutdownButton);

		JScrollPane scrollPane = new JScrollPane(textArea);
		scrollPane.setHorizontalScrollBarPolicy(ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER);
		this.scrollBar = scrollPane.getVerticalScrollBar();
		super.getContentPane().add(scrollPane, BorderLayout.CENTER);

		super.setDefaultCloseOperation(DISPOSE_ON_CLOSE);
		super.setVisible(true);
	}

	public void print(char c) {
		print(Character.toString(c), false);
	}

	public void print(int i) {
		print(Integer.toString(i));
	}

	public void print(Object object) {
		print(object.toString());
	}

	public void print(String message) {
		print(message, true);
	}

	public void print(String message, boolean newLine) {
		System.out.print(message + (newLine ? "\n" : ""));
		this.textArea.append(message + (newLine ? "\n" : ""));
		this.textArea.repaint();
		scrollBar.setValue(scrollBar.getMaximum());
	}

	public void close() {
		super.setVisible(false);
		super.dispose();
	}

	@Override
	public void dispose() {
		if (isMainConsole) {
			Main.fileServerProcess.shutdown(true);
		} else {
			process.shutdown(true);
		}
	}

	@Override
	public void actionPerformed(ActionEvent e) {
		ProcessBuilder processBuilder;
		switch (e.getActionCommand()) {
		
			case "Open Web UI":
				try {
			        Desktop.getDesktop().browse(new URL("http://127.0.0.1:8080").toURI());
			    } catch (Exception ex) {
			        ex.printStackTrace();
			    }
				break;
				
			case "Start Client":
				processBuilder = new ProcessBuilder("python", "-m", "file_server.__init__", "../test_directories/client_dir", "localhost", "test", "test");
				processBuilder.directory(new File("src"));
				
				new ConsoleProcess("File Client", processBuilder).start();
				
				break;
		
			case "Run Tests":
				processBuilder = new ProcessBuilder("test.bat");
				
				File currDir = new File(System.getProperty("user.dir"));
				if (currDir.getName() == "src") {
					processBuilder.directory(currDir.getParentFile());
				} else {
					processBuilder.directory(currDir);
				}
				new ConsoleProcess("Running Tests", processBuilder).start();
		
				break;
				
			case "Restart":
				print("Restarting console");
				process.restart();
				break;
				
			case "Shutdown":
				process.shutdown();
				break;
				
		}
	}

}
