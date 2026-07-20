using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;

namespace TheKeyPortable
{
    internal static class Program
    {
        [STAThread]
        public static void Main()
        {
            Application app = new Application();
            app.ShutdownMode = ShutdownMode.OnExplicitShutdown;

            string root = AppDomain.CurrentDomain.BaseDirectory;
            string cinematic = Path.Combine(root, "THEKEY_cinematic_loop_5s.mp4");
            if (File.Exists(cinematic))
            {
                SplashWindow splash = new SplashWindow(cinematic);
                splash.ShowDialog();
            }

            MainWindow window = new MainWindow(root);
            app.ShutdownMode = ShutdownMode.OnMainWindowClose;
            app.Run(window);
        }
    }

    internal sealed class SplashWindow : Window
    {
        private readonly MediaElement media;
        private readonly DispatcherTimer timer;

        public SplashWindow(string cinematic)
        {
            Title = "THEKEY — THE KING OF CHECKMATE";
            Width = 960;
            Height = 540;
            WindowStyle = WindowStyle.None;
            ResizeMode = ResizeMode.NoResize;
            WindowStartupLocation = WindowStartupLocation.CenterScreen;
            Background = new SolidColorBrush(Color.FromRgb(5, 8, 17));

            Grid root = new Grid();
            media = new MediaElement();
            media.Source = new Uri(cinematic, UriKind.Absolute);
            media.LoadedBehavior = MediaState.Manual;
            media.UnloadedBehavior = MediaState.Stop;
            media.Stretch = Stretch.UniformToFill;
            media.MediaEnded += delegate { CloseSafely(); };
            media.MediaFailed += delegate { CloseSafely(); };
            root.Children.Add(media);

            Border footer = new Border();
            footer.VerticalAlignment = VerticalAlignment.Bottom;
            footer.Height = 82;
            footer.Background = new LinearGradientBrush(
                Color.FromArgb(0, 5, 8, 17), Color.FromArgb(235, 5, 8, 17), 90);

            Grid footerGrid = new Grid();
            TextBlock brand = new TextBlock();
            brand.Text = "THEKEY  ·  THE KING OF CHECKMATE";
            brand.Foreground = new SolidColorBrush(Color.FromRgb(232, 190, 82));
            brand.FontSize = 20;
            brand.FontWeight = FontWeights.SemiBold;
            brand.Margin = new Thickness(28, 26, 0, 0);
            brand.VerticalAlignment = VerticalAlignment.Top;
            footerGrid.Children.Add(brand);

            Button skip = new Button();
            skip.Content = "SKIP";
            skip.Width = 86;
            skip.Height = 34;
            skip.HorizontalAlignment = HorizontalAlignment.Right;
            skip.VerticalAlignment = VerticalAlignment.Center;
            skip.Margin = new Thickness(0, 0, 24, 0);
            skip.Foreground = Brushes.White;
            skip.Background = new SolidColorBrush(Color.FromRgb(27, 38, 61));
            skip.BorderBrush = new SolidColorBrush(Color.FromRgb(232, 190, 82));
            skip.Cursor = Cursors.Hand;
            skip.Click += delegate { CloseSafely(); };
            footerGrid.Children.Add(skip);
            footer.Child = footerGrid;
            root.Children.Add(footer);

            Content = root;
            Loaded += delegate
            {
                media.Play();
                timer.Start();
            };

            timer = new DispatcherTimer();
            timer.Interval = TimeSpan.FromMilliseconds(5400);
            timer.Tick += delegate { CloseSafely(); };
        }

        private void CloseSafely()
        {
            timer.Stop();
            media.Stop();
            Close();
        }
    }

    internal sealed class MainWindow : Window
    {
        private readonly string root;
        private readonly string backend;
        private readonly TextBox output;
        private readonly TextBlock status;
        private readonly Panel actions;
        private readonly Button verifyProjectButton;
        private readonly Button repairProjectButton;
        private string selectedProject;

        public MainWindow(string applicationRoot)
        {
            root = applicationRoot;
            backend = Path.Combine(root, "core", "THEKEY-Core", "THEKEY-Core.exe");

            Title = "THEKEY — THE KING OF CHECKMATE";
            Width = 1120;
            Height = 760;
            MinWidth = 900;
            MinHeight = 650;
            WindowStartupLocation = WindowStartupLocation.CenterScreen;
            Background = new SolidColorBrush(Color.FromRgb(8, 13, 26));
            Foreground = Brushes.White;

            Grid layout = new Grid();
            layout.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            layout.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            layout.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            layout.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            Content = layout;

            Border header = BuildHeader();
            Grid.SetRow(header, 0);
            layout.Children.Add(header);

            actions = new StackPanel();
            actions.Margin = new Thickness(24, 18, 24, 8);
            actions.HorizontalAlignment = HorizontalAlignment.Center;
            actions.Children.Add(CreatePrimaryAction());

            WrapPanel essentials = new WrapPanel();
            essentials.HorizontalAlignment = HorizontalAlignment.Center;
            essentials.Margin = new Thickness(0, 7, 0, 0);
            verifyProjectButton = CreateCard("\u2713", "Verificar aplicación", "Copia aislada y gates reales", VerifySelectedApplication);
            verifyProjectButton.IsEnabled = false;
            essentials.Children.Add(verifyProjectButton);
            repairProjectButton = CreateCard("\u2692", "Escanear y reparar", "Diagnóstico, reparación y re-test", RepairSelectedApplication);
            repairProjectButton.IsEnabled = false;
            essentials.Children.Add(repairProjectButton);
            essentials.Children.Add(CreateCard("\u25B6", "Demo para jueces", "Ejemplo gobernado reproducible", RunDemo));
            essentials.Children.Add(CreateCard("\u25A3", "Ver resultados / View", "Recibos y decisiones", OpenResults));
            actions.Children.Add(essentials);

            Expander advanced = new Expander();
            advanced.Header = "Opciones avanzadas / Advanced options";
            advanced.Foreground = new SolidColorBrush(Color.FromRgb(151, 168, 198));
            advanced.Margin = new Thickness(12, 8, 12, 0);
            advanced.HorizontalAlignment = HorizontalAlignment.Center;
            WrapPanel advancedCards = new WrapPanel();
            advancedCards.HorizontalAlignment = HorizontalAlignment.Center;
            advancedCards.Children.Add(CreateCard("\u2713", "Verificar evidencia", "Revisar la última demo", VerifyEvidence));
            advancedCards.Children.Add(CreateCard("\u2605", "Ayuda / Help", "Guía rápida bilingüe", OpenGuide));
            advancedCards.Children.Add(CreateCard("\u265A", "Acceso / Shortcut", "Crear acceso en escritorio", CreateShortcut));
            advancedCards.Children.Add(CreateCard("?", "Ayuda CLI / CLI help", "Todos los comandos técnicos", ShowHelp));
            advanced.Content = advancedCards;
            actions.Children.Add(advanced);
            Grid.SetRow(actions, 1);
            layout.Children.Add(actions);

            Border consoleBorder = new Border();
            consoleBorder.Margin = new Thickness(24, 8, 24, 14);
            consoleBorder.Padding = new Thickness(1);
            consoleBorder.CornerRadius = new CornerRadius(8);
            consoleBorder.BorderBrush = new SolidColorBrush(Color.FromRgb(49, 65, 96));
            consoleBorder.BorderThickness = new Thickness(1);
            consoleBorder.Background = new SolidColorBrush(Color.FromRgb(4, 8, 17));

            output = new TextBox();
            output.IsReadOnly = true;
            output.AcceptsReturn = true;
            output.TextWrapping = TextWrapping.Wrap;
            output.VerticalScrollBarVisibility = ScrollBarVisibility.Auto;
            output.HorizontalScrollBarVisibility = ScrollBarVisibility.Auto;
            output.Background = Brushes.Transparent;
            output.Foreground = new SolidColorBrush(Color.FromRgb(214, 224, 241));
            output.BorderThickness = new Thickness(0);
            output.FontFamily = new FontFamily("Consolas");
            output.FontSize = 13;
            output.Padding = new Thickness(16);
            output.Text = "1. Selecciona una aplicación compatible.\r\n2. THEKEY la analiza sin ejecutar código.\r\n3. Verifica o escanea fallos en una copia aislada.\r\n4. Autoriza solo reparaciones que hayan pasado todos los gates.\r\n";
            consoleBorder.Child = output;
            Grid.SetRow(consoleBorder, 2);
            layout.Children.Add(consoleBorder);

            Grid footer = new Grid();
            footer.Margin = new Thickness(24, 0, 24, 18);
            footer.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            footer.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            status = new TextBlock();
            status.Text = File.Exists(backend) ? "LISTO / READY · SELECCIONA UNA APLICACIÓN · Windows 10/11" : "FALTA EL MOTOR / BACKEND MISSING";
            status.Foreground = new SolidColorBrush(Color.FromRgb(123, 220, 172));
            status.VerticalAlignment = VerticalAlignment.Center;
            footer.Children.Add(status);
            TextBlock boundary = new TextBlock();
            boundary.Text = "Reparación verificada · consentimiento explícito · backup";
            boundary.Foreground = new SolidColorBrush(Color.FromRgb(139, 153, 181));
            Grid.SetColumn(boundary, 1);
            footer.Children.Add(boundary);
            Grid.SetRow(footer, 3);
            layout.Children.Add(footer);
        }

        private Border BuildHeader()
        {
            Border border = new Border();
            border.Padding = new Thickness(32, 24, 32, 22);
            border.Background = new LinearGradientBrush(
                Color.FromRgb(15, 25, 49), Color.FromRgb(8, 13, 26), 0);
            border.BorderBrush = new SolidColorBrush(Color.FromRgb(62, 76, 105));
            border.BorderThickness = new Thickness(0, 0, 0, 1);

            Grid grid = new Grid();
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });

            Border emblem = new Border();
            emblem.Width = 68;
            emblem.Height = 68;
            emblem.CornerRadius = new CornerRadius(14);
            emblem.Background = new SolidColorBrush(Color.FromRgb(228, 184, 74));
            TextBlock king = new TextBlock();
            king.Text = "\u265A";
            king.Foreground = new SolidColorBrush(Color.FromRgb(8, 13, 26));
            king.FontSize = 46;
            king.HorizontalAlignment = HorizontalAlignment.Center;
            king.VerticalAlignment = VerticalAlignment.Center;
            emblem.Child = king;
            grid.Children.Add(emblem);

            StackPanel titles = new StackPanel();
            titles.Margin = new Thickness(20, 0, 0, 0);
            TextBlock product = new TextBlock();
            product.Text = "THEKEY";
            product.FontSize = 31;
            product.FontWeight = FontWeights.Bold;
            product.Foreground = Brushes.White;
            titles.Children.Add(product);
            TextBlock name = new TextBlock();
            name.Text = "THE KING OF CHECKMATE";
            name.FontSize = 18;
            name.FontWeight = FontWeights.SemiBold;
            name.Foreground = new SolidColorBrush(Color.FromRgb(232, 190, 82));
            titles.Children.Add(name);
            TextBlock tagline = new TextBlock();
            tagline.Text = "Governed Codex Transactions for Coding Agents";
            tagline.Margin = new Thickness(0, 5, 0, 0);
            tagline.Foreground = new SolidColorBrush(Color.FromRgb(168, 183, 210));
            tagline.FontSize = 14;
            titles.Children.Add(tagline);
            Grid.SetColumn(titles, 1);
            grid.Children.Add(titles);
            border.Child = grid;
            return border;
        }

        private Button CreateCard(string symbol, string title, string detail, RoutedEventHandler action)
        {
            Button button = new Button();
            button.Width = 258;
            button.Height = 72;
            button.Margin = new Thickness(6);
            button.Padding = new Thickness(13, 8, 13, 8);
            button.Background = new SolidColorBrush(Color.FromRgb(20, 31, 54));
            button.BorderBrush = new SolidColorBrush(Color.FromRgb(61, 79, 113));
            button.BorderThickness = new Thickness(1);
            button.Foreground = Brushes.White;
            button.Cursor = Cursors.Hand;
            button.HorizontalContentAlignment = HorizontalAlignment.Stretch;
            button.Click += action;

            Grid content = new Grid();
            content.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(50) });
            content.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            TextBlock icon = new TextBlock();
            icon.Text = symbol;
            icon.FontSize = 28;
            icon.Foreground = new SolidColorBrush(Color.FromRgb(232, 190, 82));
            icon.VerticalAlignment = VerticalAlignment.Center;
            content.Children.Add(icon);
            StackPanel copy = new StackPanel();
            copy.VerticalAlignment = VerticalAlignment.Center;
            TextBlock heading = new TextBlock();
            heading.Text = title;
            heading.FontSize = 16;
            heading.FontWeight = FontWeights.SemiBold;
            heading.Foreground = Brushes.White;
            copy.Children.Add(heading);
            TextBlock description = new TextBlock();
            description.Text = detail;
            description.FontSize = 12;
            description.Margin = new Thickness(0, 4, 0, 0);
            description.Foreground = new SolidColorBrush(Color.FromRgb(161, 176, 204));
            copy.Children.Add(description);
            Grid.SetColumn(copy, 1);
            content.Children.Add(copy);
            button.Content = content;
            return button;
        }

        private Button CreatePrimaryAction()
        {
            Button button = new Button();
            button.Width = 798;
            button.Height = 92;
            button.Margin = new Thickness(6, 0, 6, 2);
            button.Padding = new Thickness(24, 12, 24, 12);
            button.Background = new LinearGradientBrush(
                Color.FromRgb(245, 203, 92), Color.FromRgb(220, 166, 49), 0);
            button.BorderBrush = new SolidColorBrush(Color.FromRgb(255, 225, 142));
            button.BorderThickness = new Thickness(1);
            button.Foreground = new SolidColorBrush(Color.FromRgb(8, 13, 26));
            button.Cursor = Cursors.Hand;
            button.Click += SelectApplication;

            StackPanel content = new StackPanel();
            content.HorizontalAlignment = HorizontalAlignment.Center;
            content.VerticalAlignment = VerticalAlignment.Center;
            TextBlock heading = new TextBlock();
            heading.Text = "\u25A3  SELECCIONAR Y ANALIZAR APLICACIÓN";
            heading.FontSize = 22;
            heading.FontWeight = FontWeights.Bold;
            heading.HorizontalAlignment = HorizontalAlignment.Center;
            content.Children.Add(heading);
            TextBlock description = new TextBlock();
            description.Text = "Inspección de solo lectura: no ejecuta código de la aplicación";
            description.FontSize = 13;
            description.Margin = new Thickness(0, 6, 0, 0);
            description.HorizontalAlignment = HorizontalAlignment.Center;
            content.Children.Add(description);
            button.Content = content;
            return button;
        }

        private void RunDemo(object sender, RoutedEventArgs e)
        {
            RunBackend("portable-demo", "EJECUTANDO Y VERIFICANDO / RUNNING & VERIFYING");
        }

        private void SelectApplication(object sender, RoutedEventArgs e)
        {
            using (System.Windows.Forms.FolderBrowserDialog dialog = new System.Windows.Forms.FolderBrowserDialog())
            {
                dialog.Description = "Selecciona una aplicación o repositorio compatible para analizar";
                dialog.ShowNewFolderButton = false;
                if (dialog.ShowDialog() != System.Windows.Forms.DialogResult.OK)
                {
                    return;
                }
                selectedProject = dialog.SelectedPath;
            }
            output.Text = "Aplicación seleccionada / Selected application:\r\n" + selectedProject + "\r\n\r\n";
            RunBackend(
                "project inspect --source " + QuoteArgument(selectedProject),
                "ANALIZANDO SIN EJECUTAR CÓDIGO / READ-ONLY ANALYSIS",
                delegate(int exitCode, string text)
                {
                    verifyProjectButton.IsEnabled = exitCode == 0;
                    repairProjectButton.IsEnabled = exitCode == 0;
                    if (exitCode == 0)
                    {
                        SetStatus("ANÁLISIS LISTO · PUEDES VERIFICAR LA COPIA", true);
                    }
                });
        }

        private void VerifySelectedApplication(object sender, RoutedEventArgs e)
        {
            if (String.IsNullOrWhiteSpace(selectedProject))
            {
                SetStatus("SELECCIONA UNA APLICACIÓN PRIMERO", false);
                return;
            }
            MessageBoxResult answer = MessageBox.Show(
                "THEKEY copiará el proyecto a un workspace aislado y ejecutará sus tests.\n\n" +
                "Los tests son código local de confianza y NO se ejecutan dentro de un sandbox " +
                "del sistema operativo. La aplicación original permanecerá en modo solo lectura.\n\n" +
                "¿Continuar?",
                "THEKEY — Confirmación de verificación",
                MessageBoxButton.YesNo,
                MessageBoxImage.Warning);
            if (answer != MessageBoxResult.Yes)
            {
                SetStatus("VERIFICACIÓN CANCELADA", false);
                return;
            }
            RunBackend(
                "project verify --source " + QuoteArgument(selectedProject) +
                " --consent execute_trusted_tests",
                "VERIFICANDO COPIA AISLADA / VERIFYING ISOLATED COPY",
                delegate(int exitCode, string text)
                {
                    if (exitCode == 0 && text.Contains("verdict: VERIFIED"))
                    {
                        SetStatus("APLICACIÓN VERIFICADA / VERIFIED", true);
                    }
                    else if (text.Contains("NO_VERIFICABLE"))
                    {
                        SetStatus("NO VERIFICABLE · FALTAN TESTS O EVIDENCIA", false);
                    }
                    else
                    {
                        SetStatus("BLOQUEADO / BLOCKED · REVISA LOS GATES", false);
                    }
                });
        }

        private void RepairSelectedApplication(object sender, RoutedEventArgs e)
        {
            if (String.IsNullOrWhiteSpace(selectedProject))
            {
                SetStatus("SELECCIONA UNA APLICACIÓN PRIMERO", false);
                return;
            }
            MessageBoxResult answer = MessageBox.Show(
                "THEKEY ejecutará los tests de confianza en una copia aislada y buscará " +
                "una reparación acotada. Solo si compila, pasa la suite completa, el escaneo " +
                "de secretos y el gate documental, aplicará exactamente ese cambio al original.\n\n" +
                "Antes de escribir comprobará que el proyecto no haya cambiado, guardará un " +
                "backup y volverá a verificar después. Si algo falla, hará rollback.\n\n" +
                "Los tests NO están dentro de un sandbox del sistema operativo.\n\n" +
                "¿Autorizas ejecutar los tests y aplicar únicamente una reparación verificada?",
                "THEKEY — Consentimiento de reparación verificada",
                MessageBoxButton.YesNo,
                MessageBoxImage.Warning);
            if (answer != MessageBoxResult.Yes)
            {
                SetStatus("REPARACIÓN CANCELADA", false);
                return;
            }
            RunBackend(
                "project repair --source " + QuoteArgument(selectedProject) +
                " --consent execute_trusted_tests --apply-consent apply_verified_repairs",
                "ESCANEANDO Y REPARANDO EN AISLAMIENTO / SCAN & REPAIR",
                delegate(int exitCode, string text)
                {
                    if (exitCode == 0 && text.Contains("outcome: REPAIRED_AND_VERIFIED"))
                    {
                        SetStatus("REPARADA Y VERIFICADA / REPAIRED & VERIFIED", true);
                    }
                    else if (exitCode == 0 && text.Contains("outcome: NO_CHANGES_NEEDED"))
                    {
                        SetStatus("SIN FALLOS · APLICACIÓN VERIFICADA / HEALTHY", true);
                    }
                    else
                    {
                        SetStatus("BLOQUEADO · NO HAY REPARACIÓN SEGURA VERIFICADA", false);
                    }
                });
        }

        private static string QuoteArgument(string value)
        {
            return "\"" + value.Replace("\"", "\\\"") + "\"";
        }

        private void VerifyEvidence(object sender, RoutedEventArgs e)
        {
            RunBackend("portable-verify", "VERIFICANDO EVIDENCIA / VERIFYING EVIDENCE");
        }

        private void ShowHelp(object sender, RoutedEventArgs e)
        {
            RunBackend("--help", "CARGANDO AYUDA / LOADING HELP");
        }

        private void OpenResults(object sender, RoutedEventArgs e)
        {
            string results = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "THEKEY",
                ".thekey");
            if (!Directory.Exists(results))
            {
                SetStatus("EJECUTA UNA VERIFICACIÓN / RUN A VERIFICATION", false);
                output.AppendText("Todavía no hay resultados / No results yet. Analiza una aplicación o ejecuta la demo.\r\n");
                return;
            }
            Process.Start("explorer.exe", "\"" + results + "\"");
            SetStatus("RESULTADOS ABIERTOS / RESULTS OPENED", true);
        }

        private void OpenGuide(object sender, RoutedEventArgs e)
        {
            string guide = Path.Combine(root, "README-FIRST.txt");
            if (!File.Exists(guide))
            {
                SetStatus("FALTA LA GUÍA / GUIDE MISSING", false);
                return;
            }
            Process.Start(new ProcessStartInfo(guide) { UseShellExecute = true });
            SetStatus("GUÍA ABIERTA / GUIDE OPENED", true);
        }

        private void CreateShortcut(object sender, RoutedEventArgs e)
        {
            try
            {
                string desktop = Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);
                string link = Path.Combine(desktop, "THEKEY - THE KING OF CHECKMATE.lnk");
                Type shellType = Type.GetTypeFromProgID("WScript.Shell");
                dynamic shell = Activator.CreateInstance(shellType);
                dynamic shortcut = shell.CreateShortcut(link);
                shortcut.TargetPath = Process.GetCurrentProcess().MainModule.FileName;
                shortcut.WorkingDirectory = root;
                shortcut.Description = "THEKEY — Governed Codex Transactions for Coding Agents";
                shortcut.IconLocation = Process.GetCurrentProcess().MainModule.FileName + ",0";
                shortcut.Save();
                SetStatus("ACCESO DIRECTO CREADO / SHORTCUT CREATED", true);
                output.AppendText("Acceso directo creado / Desktop shortcut created: " + link + "\r\n");
            }
            catch (Exception ex)
            {
                SetStatus("ERROR DE ACCESO / SHORTCUT FAILED", false);
                output.AppendText("Error del acceso directo / Shortcut error: " + ex.Message + "\r\n");
            }
        }

        private void RunBackend(string arguments, string runningStatus)
        {
            RunBackend(arguments, runningStatus, null);
        }

        private void RunBackend(
            string arguments,
            string runningStatus,
            Action<int, string> completed)
        {
            if (!File.Exists(backend))
            {
                SetStatus("FALTA EL MOTOR / BACKEND MISSING", false);
                output.AppendText("Falta el motor / Missing backend: " + backend + "\r\n");
                return;
            }
            SetActionsEnabled(false);
            SetStatus(runningStatus, true);
            output.Text = "> THEKEY-Core.exe " + arguments + "\r\n\r\n";

            Task.Factory.StartNew(delegate
            {
                int exitCode = 1;
                string combined;
                try
                {
                    ProcessStartInfo info = new ProcessStartInfo();
                    info.FileName = backend;
                    info.Arguments = arguments;
                    info.WorkingDirectory = Path.GetDirectoryName(backend);
                    info.UseShellExecute = false;
                    info.CreateNoWindow = true;
                    info.RedirectStandardOutput = true;
                    info.RedirectStandardError = true;
                    info.StandardOutputEncoding = Encoding.UTF8;
                    info.StandardErrorEncoding = Encoding.UTF8;
                    using (Process process = Process.Start(info))
                    {
                        string stdout = process.StandardOutput.ReadToEnd();
                        string stderr = process.StandardError.ReadToEnd();
                        process.WaitForExit();
                        exitCode = process.ExitCode;
                        combined = stdout + (String.IsNullOrWhiteSpace(stderr) ? "" : "\r\n" + stderr);
                    }
                }
                catch (Exception ex)
                {
                    combined = "Launcher error: " + ex.Message;
                }

                Dispatcher.Invoke(delegate
                {
                    output.AppendText(combined.Trim() + "\r\n\r\nExit code: " + exitCode + "\r\n");
                    output.ScrollToEnd();
                    SetStatus(exitCode == 0 ? "PASS · VERIFICADO / VERIFIED" : "FALLO / FAILED", exitCode == 0);
                    SetActionsEnabled(true);
                    if (completed != null)
                    {
                        completed(exitCode, combined);
                    }
                });
            });
        }

        private void SetActionsEnabled(bool enabled)
        {
            foreach (UIElement child in actions.Children)
            {
                child.IsEnabled = enabled;
            }
        }

        private void SetStatus(string value, bool ok)
        {
            status.Text = value;
            status.Foreground = new SolidColorBrush(
                ok ? Color.FromRgb(123, 220, 172) : Color.FromRgb(255, 126, 126));
        }
    }
}
