using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Automation;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Media.Effects;
using System.Windows.Media.Imaging;
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
            bool skipSplash = String.Equals(
                Environment.GetEnvironmentVariable("THEKEY_SKIP_SPLASH"),
                "1",
                StringComparison.Ordinal);
            if (File.Exists(cinematic) && !skipSplash)
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
            skip.Content = "OMITIR / SKIP";
            skip.Width = 118;
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
        private TextBlock sourceState;
        private TextBlock recentActivity;
        private TextBlock recentTime;
        private TextBlock recentType;
        private TextBlock recentState;
        private readonly Panel actions;
        private readonly Button verifyProjectButton;
        private readonly Button repairProjectButton;
        private string selectedProject;

        public MainWindow(string applicationRoot)
        {
            root = applicationRoot;
            backend = Path.Combine(root, "core", "THEKEY-Core", "THEKEY-Core.exe");
            string referencePath = Path.Combine(root, "THEKEY_UI_REFERENCE.png");
            if (!File.Exists(referencePath))
            {
                throw new FileNotFoundException("Missing canonical UI reference", referencePath);
            }

            BitmapImage reference = new BitmapImage();
            reference.BeginInit();
            reference.CacheOption = BitmapCacheOption.OnLoad;
            reference.CreateOptions = BitmapCreateOptions.PreservePixelFormat;
            reference.UriSource = new Uri(referencePath, UriKind.Absolute);
            reference.EndInit();
            reference.Freeze();

            double referenceWidth = reference.PixelWidth;
            double referenceHeight = reference.PixelHeight;
            Rect workAreaBounds = SystemParameters.WorkArea;
            bool forceNative = String.Equals(
                Environment.GetEnvironmentVariable("THEKEY_NATIVE_UI"),
                "1",
                StringComparison.Ordinal);
            double fitScale = Math.Min(
                1.0,
                Math.Min(
                    Math.Max(1.0, workAreaBounds.Width - 24.0) / referenceWidth,
                    Math.Max(1.0, workAreaBounds.Height - 24.0) / referenceHeight));
            double initialScale = forceNative ? 1.0 : fitScale;

            Title = "THEKEY — THE KING OF CHECKMATE";
            Width = Math.Round(referenceWidth * initialScale);
            Height = Math.Round(referenceHeight * initialScale);
            MinWidth = Math.Min(724, Width);
            MinHeight = Math.Min(543, Height);
            WindowStartupLocation = WindowStartupLocation.Manual;
            Left = workAreaBounds.Left + Math.Max(0, (workAreaBounds.Width - Width) / 2);
            Top = workAreaBounds.Top + Math.Max(0, (workAreaBounds.Height - Height) / 2);
            WindowStyle = WindowStyle.None;
            ResizeMode = ResizeMode.CanResize;
            UseLayoutRounding = true;
            SnapsToDevicePixels = true;
            Background = new SolidColorBrush(Color.FromRgb(4, 7, 12));

            string appIconPath = Path.Combine(root, "THEKEY_app_icon.png");
            if (File.Exists(appIconPath))
            {
                Icon = BitmapFrame.Create(new Uri(appIconPath, UriKind.Absolute));
            }

            Grid letterbox = new Grid();
            letterbox.Background = new SolidColorBrush(Color.FromRgb(4, 7, 12));
            Content = letterbox;

            Viewbox scaler = new Viewbox();
            scaler.Stretch = Stretch.Uniform;
            scaler.StretchDirection = StretchDirection.Both;
            scaler.HorizontalAlignment = HorizontalAlignment.Stretch;
            scaler.VerticalAlignment = VerticalAlignment.Stretch;
            letterbox.Children.Add(scaler);

            Canvas composition = new Canvas();
            composition.Width = referenceWidth;
            composition.Height = referenceHeight;
            composition.SnapsToDevicePixels = true;
            scaler.Child = composition;

            Image background = new Image();
            background.Source = reference;
            background.Width = referenceWidth;
            background.Height = referenceHeight;
            background.Stretch = Stretch.Fill;
            background.SnapsToDevicePixels = true;
            RenderOptions.SetEdgeMode(background, EdgeMode.Aliased);
            Canvas.SetLeft(background, 0);
            Canvas.SetTop(background, 0);
            composition.Children.Add(background);

            actions = new Canvas
            {
                Width = referenceWidth,
                Height = referenceHeight,
                Background = Brushes.Transparent
            };
            Panel.SetZIndex(actions, 10);
            composition.Children.Add(actions);

            AddHotspot(actions, "Inicio / Home", 0, 244, 235, 65, ShowHome);
            AddHotspot(actions, "Analizar / Analyze", 17, 310, 214, 69, SelectApplication);
            AddHotspot(actions, "Herramientas / Tools", 17, 380, 214, 69, ShowHelp);
            AddHotspot(actions, "Resultados / Results", 17, 450, 214, 69, OpenResults);
            AddHotspot(actions, "Modos / Modes", 17, 520, 214, 69, ShowUpcomingMode);
            AddHotspot(actions, "Registros / Logs", 17, 590, 214, 69, OpenResults);
            AddHotspot(actions, "Ajustes / Settings", 17, 660, 214, 69, OpenGuide);

            AddHotspot(actions, "Seleccionar y analizar / Select & Analyze", 300, 284, 692, 111, SelectApplication);
            verifyProjectButton = AddHotspot(actions, "Verificar / Verify", 265, 417, 219, 253, VerifySelectedApplication);
            repairProjectButton = AddHotspot(actions, "Reparar / Repair", 496, 417, 211, 253, RepairSelectedApplication);
            AddHotspot(actions, "Demo para jueces / Judge demo", 719, 417, 210, 253, RunDemo);
            AddHotspot(actions, "Ver resultados / View results", 942, 417, 208, 253, OpenResults);
            AddHotspot(actions, "THE KING", 264, 716, 438, 103, ShowUpcomingMode);
            AddHotspot(actions, "CHECKMATE", 712, 716, 438, 103, ShowUpcomingMode);
            AddHotspot(actions, "Ver todos / View all", 1215, 832, 210, 37, OpenResults);
            verifyProjectButton.IsEnabled = false;
            repairProjectButton.IsEnabled = false;

            Border dragRegion = new Border();
            dragRegion.Width = 1274;
            dragRegion.Height = 48;
            dragRegion.Background = Brushes.Transparent;
            dragRegion.Cursor = Cursors.SizeAll;
            dragRegion.MouseLeftButtonDown += delegate(object sender, MouseButtonEventArgs e)
            {
                if (e.ClickCount == 2)
                {
                    ToggleMaximize();
                }
                else
                {
                    DragMove();
                }
            };
            Panel.SetZIndex(dragRegion, 20);
            composition.Children.Add(dragRegion);

            AddWindowHotspot(composition, "Minimizar / Minimize", 1274, 0, 54, 48, delegate { WindowState = WindowState.Minimized; });
            AddWindowHotspot(composition, "Maximizar / Maximize", 1328, 0, 55, 48, ToggleMaximize);
            AddWindowHotspot(composition, "Cerrar / Close", 1383, 0, 65, 48, Close);

            output = new TextBox();
            output.IsReadOnly = true;
            output.Text = "THEKEY listo / ready. Selecciona una aplicación para comenzar / Select an application to begin.\r\n";
            status = new TextBlock();
            status.Text = File.Exists(backend) ? "LISTO / READY" : "FALTA EL MOTOR / BACKEND MISSING";

            string verificationCapture = Environment.GetEnvironmentVariable("THEKEY_CAPTURE_PATH");
            if (!String.IsNullOrWhiteSpace(verificationCapture))
            {
                Loaded += delegate
                {
                    Dispatcher.BeginInvoke(
                        DispatcherPriority.ApplicationIdle,
                        new Action(delegate
                        {
                            CaptureComposition(
                                composition,
                                (int)referenceWidth,
                                (int)referenceHeight,
                                verificationCapture);
                            Close();
                        }));
                };
            }
        }

        private static void CaptureComposition(
            FrameworkElement composition,
            int width,
            int height,
            string outputPath)
        {
            string directory = Path.GetDirectoryName(outputPath);
            if (!String.IsNullOrWhiteSpace(directory))
            {
                Directory.CreateDirectory(directory);
            }
            composition.UpdateLayout();
            RenderTargetBitmap rendered = new RenderTargetBitmap(
                width,
                height,
                96,
                96,
                PixelFormats.Pbgra32);
            rendered.Render(composition);
            PngBitmapEncoder encoder = new PngBitmapEncoder();
            encoder.Frames.Add(BitmapFrame.Create(rendered));
            using (FileStream stream = File.Create(outputPath))
            {
                encoder.Save(stream);
            }
        }

        private static Button AddHotspot(
            Panel host,
            string accessibleName,
            double x,
            double y,
            double width,
            double height,
            RoutedEventHandler action)
        {
            Button button = CreateTransparentButton(accessibleName, width, height);
            button.Click += action;
            Canvas.SetLeft(button, x);
            Canvas.SetTop(button, y);
            host.Children.Add(button);
            return button;
        }

        private static void AddWindowHotspot(
            Canvas host,
            string accessibleName,
            double x,
            double y,
            double width,
            double height,
            Action action)
        {
            Button button = CreateTransparentButton(accessibleName, width, height);
            button.Click += delegate { action(); };
            Canvas.SetLeft(button, x);
            Canvas.SetTop(button, y);
            Panel.SetZIndex(button, 30);
            host.Children.Add(button);
        }

        private static Button CreateTransparentButton(string accessibleName, double width, double height)
        {
            Button button = new Button();
            button.Width = width;
            button.Height = height;
            button.Background = Brushes.Transparent;
            button.BorderThickness = new Thickness(0);
            button.FocusVisualStyle = null;
            button.Cursor = Cursors.Hand;
            button.Template = CreateTransparentTemplate();
            AutomationProperties.SetName(button, accessibleName);
            return button;
        }

        private static ControlTemplate CreateTransparentTemplate()
        {
            ControlTemplate template = new ControlTemplate(typeof(Button));
            FrameworkElementFactory hitSurface = new FrameworkElementFactory(typeof(Border));
            hitSurface.SetValue(Border.BackgroundProperty, Brushes.Transparent);
            template.VisualTree = hitSurface;
            return template;
        }

        private void ToggleMaximize()
        {
            WindowState = WindowState == WindowState.Maximized
                ? WindowState.Normal
                : WindowState.Maximized;
        }

        private void ShowHome(object sender, RoutedEventArgs e)
        {
            SetStatus("INICIO / HOME", true);
        }

        private void ShowUpcomingMode(object sender, RoutedEventArgs e)
        {
            MessageBox.Show(
                "PRÓXIMAMENTE / SOON",
                "THEKEY",
                MessageBoxButton.OK,
                MessageBoxImage.Information);
        }

        private Border BuildTitleBar()
        {
            Border bar = new Border();
            bar.Background = new SolidColorBrush(Color.FromRgb(5, 12, 23));
            bar.BorderBrush = new SolidColorBrush(Color.FromRgb(125, 91, 30));
            bar.BorderThickness = new Thickness(0, 0, 0, 1);
            bar.MouseLeftButtonDown += delegate(object sender, MouseButtonEventArgs e)
            {
                if (e.ClickCount == 2)
                {
                    WindowState = WindowState == WindowState.Maximized
                        ? WindowState.Normal : WindowState.Maximized;
                }
                else
                {
                    DragMove();
                }
            };
            Grid grid = new Grid();
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            StackPanel brand = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(18, 0, 0, 0) };
            brand.Children.Add(CreateBrandIcon(25));
            TextBlock title = new TextBlock
            {
                Text = "THEKEY  —  THE KING OF CHECKMATE",
                Margin = new Thickness(10, 0, 0, 0),
                FontSize = 12,
                FontWeight = FontWeights.SemiBold,
                Foreground = new SolidColorBrush(Color.FromRgb(221, 225, 234)),
                VerticalAlignment = VerticalAlignment.Center
            };
            brand.Children.Add(title);
            grid.Children.Add(brand);
            StackPanel controls = new StackPanel { Orientation = Orientation.Horizontal };
            controls.Children.Add(CreateWindowButton("—", delegate { WindowState = WindowState.Minimized; }));
            controls.Children.Add(CreateWindowButton("□", delegate
            {
                WindowState = WindowState == WindowState.Maximized ? WindowState.Normal : WindowState.Maximized;
            }));
            controls.Children.Add(CreateWindowButton("×", delegate { Close(); }));
            Grid.SetColumn(controls, 1);
            grid.Children.Add(controls);
            bar.Child = grid;
            return bar;
        }

        private Button CreateWindowButton(string label, Action action)
        {
            Button button = new Button
            {
                Content = label,
                Width = 48,
                Height = 47,
                Foreground = new SolidColorBrush(Color.FromRgb(198, 205, 218)),
                Background = Brushes.Transparent,
                BorderThickness = new Thickness(0),
                FontSize = 18,
                Cursor = Cursors.Hand
            };
            button.Click += delegate(object sender, RoutedEventArgs e)
            {
                e.Handled = true;
                action();
            };
            return button;
        }

        private Border BuildSidebar()
        {
            Border sidebar = new Border();
            sidebar.Background = new LinearGradientBrush(
                Color.FromRgb(8, 19, 34), Color.FromRgb(4, 13, 25), 90);
            sidebar.BorderBrush = new SolidColorBrush(Color.FromRgb(107, 78, 29));
            sidebar.BorderThickness = new Thickness(0, 0, 1, 0);
            Grid layout = new Grid();
            layout.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            layout.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            layout.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            StackPanel identity = new StackPanel { Margin = new Thickness(20, 22, 20, 20) };
            Border seal = new Border
            {
                Width = 76,
                Height = 76,
                CornerRadius = new CornerRadius(38),
                BorderBrush = new SolidColorBrush(Color.FromRgb(151, 110, 38)),
                BorderThickness = new Thickness(1),
                Background = new SolidColorBrush(Color.FromArgb(80, 32, 24, 11)),
                HorizontalAlignment = HorizontalAlignment.Center
            };
            seal.Child = CreateBrandIcon(68);
            identity.Children.Add(seal);
            identity.Children.Add(new TextBlock
            {
                Text = "THEKEY",
                FontFamily = new FontFamily("Georgia"),
                FontSize = 24,
                Foreground = new SolidColorBrush(Color.FromRgb(239, 200, 112)),
                HorizontalAlignment = HorizontalAlignment.Center,
                Margin = new Thickness(0, 9, 0, 0)
            });
            identity.Children.Add(new TextBlock
            {
                Text = "THE KING OF CHECKMATE",
                FontSize = 9,
                Foreground = new SolidColorBrush(Color.FromRgb(190, 159, 99)),
                HorizontalAlignment = HorizontalAlignment.Center
            });
            layout.Children.Add(identity);

            StackPanel navigation = new StackPanel { Margin = new Thickness(12, 0, 12, 0) };
            navigation.Children.Add(CreateNavButton("⌂", "Inicio / Home", true, delegate { SetStatus("INICIO / HOME", true); }));
            navigation.Children.Add(CreateNavButton("⌕", "Analizar / Analyze", false, SelectApplication));
            Expander tools = new Expander
            {
                Header = "⚒   Herramientas / Tools",
                Foreground = new SolidColorBrush(Color.FromRgb(190, 199, 215)),
                FontSize = 13,
                Margin = new Thickness(10, 5, 10, 5)
            };
            StackPanel toolItems = new StackPanel { Margin = new Thickness(14, 5, 0, 5) };
            toolItems.Children.Add(CreateSideUtility("Verificar evidencia / Verify evidence", VerifyEvidence));
            toolItems.Children.Add(CreateSideUtility("Crear acceso / Create shortcut", CreateShortcut));
            toolItems.Children.Add(CreateSideUtility("Ayuda CLI / CLI help", ShowHelp));
            tools.Content = toolItems;
            navigation.Children.Add(tools);
            navigation.Children.Add(CreateNavButton("▥", "Resultados / Results", false, OpenResults));
            navigation.Children.Add(CreateNavButton("♛", "Modos / Modes", false, delegate { SetStatus("THE KING Y CHECKMATE · PRÓXIMAMENTE / COMING SOON", true); }));
            navigation.Children.Add(CreateNavButton("▤", "Registros / Logs", false, OpenResults));
            navigation.Children.Add(CreateNavButton("⚙", "Ajustes / Settings", false, OpenGuide));
            Grid.SetRow(navigation, 1);
            layout.Children.Add(navigation);

            Border health = new Border
            {
                Margin = new Thickness(16, 12, 16, 18),
                Padding = new Thickness(15, 12, 15, 12),
                CornerRadius = new CornerRadius(10),
                Background = new SolidColorBrush(Color.FromRgb(8, 20, 32)),
                BorderBrush = new SolidColorBrush(Color.FromRgb(86, 70, 40)),
                BorderThickness = new Thickness(1)
            };
            StackPanel healthCopy = new StackPanel();
            healthCopy.Children.Add(new TextBlock
            {
                Text = File.Exists(backend) ? "✓  LISTO / READY" : "!  MOTOR NO DISPONIBLE",
                Foreground = File.Exists(backend) ? new SolidColorBrush(Color.FromRgb(82, 231, 125)) : new SolidColorBrush(Color.FromRgb(255, 126, 126)),
                FontSize = 13,
                FontWeight = FontWeights.SemiBold
            });
            healthCopy.Children.Add(new TextBlock
            {
                Text = "Motor local / Local engine",
                Foreground = new SolidColorBrush(Color.FromRgb(142, 158, 184)),
                FontSize = 10,
                Margin = new Thickness(23, 4, 0, 0)
            });
            health.Child = healthCopy;
            Grid.SetRow(health, 2);
            layout.Children.Add(health);
            sidebar.Child = layout;
            return sidebar;
        }

        private FrameworkElement CreateBrandIcon(double size)
        {
            string path = Path.Combine(root, "THEKEY_app_icon.png");
            if (File.Exists(path))
            {
                return new Image
                {
                    Source = new BitmapImage(new Uri(path, UriKind.Absolute)),
                    Width = size,
                    Height = size,
                    Stretch = Stretch.Uniform,
                    HorizontalAlignment = HorizontalAlignment.Center,
                    VerticalAlignment = VerticalAlignment.Center
                };
            }
            return new TextBlock
            {
                Text = "\u265A",
                FontSize = size * 0.72,
                Foreground = new SolidColorBrush(Color.FromRgb(231, 180, 70)),
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center
            };
        }

        private Button CreateNavButton(string symbol, string label, bool selected, RoutedEventHandler action)
        {
            Button button = new Button
            {
                Height = 55,
                Margin = new Thickness(0, 2, 0, 2),
                Padding = new Thickness(12, 0, 12, 0),
                HorizontalContentAlignment = HorizontalAlignment.Left,
                Background = selected ? new SolidColorBrush(Color.FromRgb(16, 29, 47)) : Brushes.Transparent,
                BorderBrush = selected ? new SolidColorBrush(Color.FromRgb(103, 77, 35)) : new SolidColorBrush(Color.FromRgb(27, 40, 59)),
                BorderThickness = selected ? new Thickness(1) : new Thickness(0, 0, 0, 1),
                Foreground = selected ? new SolidColorBrush(Color.FromRgb(235, 191, 92)) : new SolidColorBrush(Color.FromRgb(175, 186, 204)),
                Cursor = Cursors.Hand
            };
            StackPanel content = new StackPanel { Orientation = Orientation.Horizontal };
            content.Children.Add(new TextBlock { Text = symbol, FontSize = 22, Width = 37, VerticalAlignment = VerticalAlignment.Center });
            content.Children.Add(new TextBlock { Text = label, FontSize = 13, VerticalAlignment = VerticalAlignment.Center });
            button.Content = content;
            button.Click += action;
            AutomationProperties.SetName(button, label);
            return button;
        }

        private Button CreateSideUtility(string label, RoutedEventHandler action)
        {
            Button button = new Button
            {
                Content = label,
                Height = 31,
                Margin = new Thickness(0, 2, 0, 2),
                HorizontalContentAlignment = HorizontalAlignment.Left,
                Foreground = new SolidColorBrush(Color.FromRgb(151, 168, 194)),
                Background = Brushes.Transparent,
                BorderThickness = new Thickness(0),
                FontSize = 10,
                Cursor = Cursors.Hand
            };
            button.Click += action;
            return button;
        }

        private Border BuildHero()
        {
            Border hero = new Border
            {
                Height = 222,
                CornerRadius = new CornerRadius(12),
                BorderBrush = new SolidColorBrush(Color.FromRgb(87, 65, 31)),
                BorderThickness = new Thickness(1),
                ClipToBounds = true
            };
            hero.Background = new LinearGradientBrush(Color.FromRgb(8, 20, 37), Color.FromRgb(4, 9, 18), 0);
            Grid overlay = new Grid();
            string heroPath = Path.Combine(root, "THEKEY_hero_chess.png");
            if (File.Exists(heroPath))
            {
                Image art = new Image
                {
                    Source = new BitmapImage(new Uri(heroPath, UriKind.Absolute)),
                    Stretch = Stretch.Uniform,
                    Width = 560,
                    HorizontalAlignment = HorizontalAlignment.Right,
                    VerticalAlignment = VerticalAlignment.Center
                };
                overlay.Children.Add(art);
            }
            Border shade = new Border
            {
                Background = new LinearGradientBrush(
                    Color.FromArgb(245, 3, 11, 23),
                    Color.FromArgb(32, 3, 11, 23), 0)
            };
            overlay.Children.Add(shade);
            StackPanel copy = new StackPanel
            {
                Margin = new Thickness(34, 25, 0, 0),
                Width = 610,
                HorizontalAlignment = HorizontalAlignment.Left,
                VerticalAlignment = VerticalAlignment.Top
            };
            copy.Children.Add(new TextBlock
            {
                Text = "Bienvenido / Welcome",
                FontSize = 16,
                Foreground = new SolidColorBrush(Color.FromRgb(229, 181, 76))
            });
            copy.Children.Add(new TextBlock
            {
                Text = "THEKEY",
                FontFamily = new FontFamily("Georgia"),
                FontSize = 46,
                Foreground = Brushes.White,
                Margin = new Thickness(0, 3, 0, 0)
            });
            copy.Children.Add(new TextBlock
            {
                Text = "THE KING OF CHECKMATE",
                FontFamily = new FontFamily("Georgia"),
                FontSize = 17,
                Foreground = new SolidColorBrush(Color.FromRgb(230, 179, 69)),
                Margin = new Thickness(2, 1, 0, 0)
            });
            copy.Children.Add(new TextBlock
            {
                Text = "Análisis, verificación y reparación gobernada de aplicaciones.\nGoverned application analysis, verification and repair.",
                FontSize = 13,
                FontStyle = FontStyles.Italic,
                Foreground = new SolidColorBrush(Color.FromRgb(196, 204, 218)),
                Margin = new Thickness(0, 14, 0, 0),
                LineHeight = 20
            });
            overlay.Children.Add(copy);
            Border local = new Border
            {
                HorizontalAlignment = HorizontalAlignment.Right,
                VerticalAlignment = VerticalAlignment.Top,
                Margin = new Thickness(0, 22, 22, 0),
                Padding = new Thickness(13, 8, 13, 8),
                CornerRadius = new CornerRadius(18),
                Background = new SolidColorBrush(Color.FromArgb(215, 5, 20, 31)),
                BorderBrush = new SolidColorBrush(Color.FromRgb(55, 91, 102)),
                BorderThickness = new Thickness(1)
            };
            local.Child = new TextBlock
            {
                Text = "♢  Modo local / Local mode   ●",
                Foreground = new SolidColorBrush(Color.FromRgb(92, 232, 132)),
                FontSize = 11,
                FontWeight = FontWeights.SemiBold
            };
            overlay.Children.Add(local);
            hero.Child = overlay;
            return hero;
        }

        private Border BuildSystemPanel()
        {
            Border panel = new Border
            {
                Padding = new Thickness(18),
                CornerRadius = new CornerRadius(12),
                Background = new LinearGradientBrush(Color.FromRgb(10, 25, 41), Color.FromRgb(5, 15, 28), 90),
                BorderBrush = new SolidColorBrush(Color.FromRgb(111, 82, 35)),
                BorderThickness = new Thickness(1)
            };
            StackPanel content = new StackPanel();
            content.Children.Add(new TextBlock
            {
                Text = "ESTADO DEL SISTEMA\nSYSTEM STATUS",
                FontSize = 12,
                Foreground = new SolidColorBrush(Color.FromRgb(226, 182, 84)),
                LineHeight = 18
            });
            Grid gauge = new Grid
            {
                Width = 146,
                Height = 146,
                Margin = new Thickness(0, 15, 0, 5),
                HorizontalAlignment = HorizontalAlignment.Center
            };
            Canvas ticks = new Canvas { Width = 146, Height = 146 };
            for (int i = 0; i < 25; i++)
            {
                Border tick = new Border
                {
                    Width = 3,
                    Height = 11,
                    CornerRadius = new CornerRadius(1.5),
                    Background = new SolidColorBrush(
                        i < 18 ? Color.FromRgb(86, 220, 108) : Color.FromRgb(209, 183, 61)),
                    Opacity = i < 22 ? 0.85 : 0.28
                };
                Canvas.SetLeft(tick, 71.5);
                Canvas.SetTop(tick, 4);
                tick.RenderTransform = new RotateTransform(-120 + (240.0 * i / 24.0), 1.5, 69);
                ticks.Children.Add(tick);
            }
            gauge.Children.Add(ticks);
            Border ring = new Border
            {
                Width = 94,
                Height = 94,
                CornerRadius = new CornerRadius(47),
                BorderBrush = File.Exists(backend) ? new SolidColorBrush(Color.FromRgb(101, 220, 112)) : new SolidColorBrush(Color.FromRgb(255, 126, 126)),
                BorderThickness = new Thickness(3),
                Background = new SolidColorBrush(Color.FromArgb(55, 61, 150, 85)),
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
                Effect = new DropShadowEffect { Color = Color.FromRgb(99, 220, 111), BlurRadius = 22, ShadowDepth = 0, Opacity = 0.3 }
            };
            ring.Child = new TextBlock
            {
                Text = File.Exists(backend) ? "✓" : "!",
                FontSize = 46,
                Foreground = File.Exists(backend) ? new SolidColorBrush(Color.FromRgb(119, 236, 130)) : new SolidColorBrush(Color.FromRgb(255, 126, 126)),
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center
            };
            gauge.Children.Add(ring);
            content.Children.Add(gauge);
            content.Children.Add(new TextBlock
            {
                Text = File.Exists(backend) ? "LISTO / READY" : "BLOQUEADO / BLOCKED",
                FontSize = 17,
                FontWeight = FontWeights.SemiBold,
                Foreground = File.Exists(backend) ? new SolidColorBrush(Color.FromRgb(83, 231, 126)) : new SolidColorBrush(Color.FromRgb(255, 126, 126)),
                HorizontalAlignment = HorizontalAlignment.Center
            });
            content.Children.Add(new TextBlock
            {
                Text = File.Exists(backend) ? "Motor local disponible\nLocal engine available" : "Falta el motor local\nLocal engine missing",
                FontSize = 11,
                Foreground = new SolidColorBrush(Color.FromRgb(161, 174, 195)),
                TextAlignment = TextAlignment.Center,
                Margin = new Thickness(0, 7, 0, 18)
            });
            content.Children.Add(CreateStatusLine("✓", "Integridad / Integrity", "Verificada / Verified"));
            content.Children.Add(CreateStatusLine("✓", "Red / Network", "No requerida / Not required"));
            sourceState = CreateStatusLine("○", "Aplicación / Application", "Sin seleccionar / Not selected");
            content.Children.Add(sourceState);
            panel.Child = content;
            return panel;
        }

        private TextBlock CreateStatusLine(string mark, string label, string value)
        {
            return new TextBlock
            {
                Text = mark + "  " + label + "\n     " + value,
                FontSize = 10,
                Foreground = new SolidColorBrush(Color.FromRgb(153, 169, 194)),
                Margin = new Thickness(0, 6, 0, 6),
                LineHeight = 15
            };
        }

        private Border BuildActivityPanel()
        {
            Border panel = new Border
            {
                CornerRadius = new CornerRadius(10),
                Background = new SolidColorBrush(Color.FromRgb(7, 19, 33)),
                BorderBrush = new SolidColorBrush(Color.FromRgb(44, 62, 88)),
                BorderThickness = new Thickness(1)
            };
            Grid layout = new Grid();
            layout.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            layout.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            layout.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            Border header = new Border
            {
                Padding = new Thickness(16, 9, 16, 9),
                Background = new SolidColorBrush(Color.FromRgb(13, 29, 49)),
                BorderBrush = new SolidColorBrush(Color.FromRgb(43, 60, 86)),
                BorderThickness = new Thickness(0, 0, 0, 1)
            };
            header.Child = new TextBlock
            {
                Text = "ACTIVIDAD RECIENTE / RECENT ACTIVITY",
                FontSize = 11,
                Foreground = new SolidColorBrush(Color.FromRgb(191, 202, 220))
            };
            layout.Children.Add(header);
            Grid columns = CreateActivityGrid();
            columns.Background = new SolidColorBrush(Color.FromRgb(9, 22, 38));
            columns.Children.Add(CreateActivityCell("Hora / Time", 0, true));
            columns.Children.Add(CreateActivityCell("Tipo / Type", 1, true));
            columns.Children.Add(CreateActivityCell("Actividad / Activity", 2, true));
            columns.Children.Add(CreateActivityCell("Estado / Status", 3, true));
            Grid.SetRow(columns, 1);
            layout.Children.Add(columns);

            Grid row = CreateActivityGrid();
            row.Margin = new Thickness(0, 1, 0, 0);
            recentTime = CreateActivityCell("--:--:--", 0, false);
            recentType = CreateActivityCell("Sistema / System", 1, false);
            recentActivity = CreateActivityCell("Sin actividad todavía / No activity yet", 2, false);
            recentState = CreateActivityCell("Esperando / Waiting", 3, false);
            recentState.Foreground = new SolidColorBrush(Color.FromRgb(216, 177, 83));
            row.Children.Add(recentTime);
            row.Children.Add(recentType);
            row.Children.Add(recentActivity);
            row.Children.Add(recentState);
            Grid.SetRow(row, 2);
            layout.Children.Add(row);
            panel.Child = layout;
            return panel;
        }

        private Grid CreateActivityGrid()
        {
            Grid grid = new Grid { MinHeight = 34 };
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(125) });
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(170) });
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(150) });
            return grid;
        }

        private TextBlock CreateActivityCell(string text, int column, bool header)
        {
            TextBlock cell = new TextBlock
            {
                Text = text,
                Padding = new Thickness(14, 9, 10, 8),
                FontSize = header ? 10 : 11,
                FontWeight = header ? FontWeights.SemiBold : FontWeights.Normal,
                Foreground = new SolidColorBrush(
                    header ? Color.FromRgb(139, 156, 182) : Color.FromRgb(185, 197, 216)),
                TextTrimming = TextTrimming.CharacterEllipsis
            };
            Grid.SetColumn(cell, column);
            return cell;
        }

        private Border BuildHeader()
        {
            Border border = new Border();
            border.Padding = new Thickness(32, 18, 32, 17);
            border.Background = new LinearGradientBrush(
                Color.FromRgb(18, 29, 54), Color.FromRgb(8, 14, 28), 0);
            border.BorderBrush = new SolidColorBrush(Color.FromRgb(45, 61, 91));
            border.BorderThickness = new Thickness(0, 0, 0, 1);

            Grid grid = new Grid();
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });

            Border emblem = new Border();
            emblem.Width = 62;
            emblem.Height = 62;
            emblem.CornerRadius = new CornerRadius(16);
            emblem.Background = new LinearGradientBrush(
                Color.FromRgb(249, 207, 92), Color.FromRgb(214, 159, 42), 45);
            emblem.Effect = new DropShadowEffect
            {
                Color = Color.FromRgb(232, 190, 82),
                BlurRadius = 18,
                ShadowDepth = 0,
                Opacity = 0.22
            };
            TextBlock king = new TextBlock();
            king.Text = "\u265A";
            king.Foreground = new SolidColorBrush(Color.FromRgb(8, 13, 26));
            king.FontSize = 40;
            king.HorizontalAlignment = HorizontalAlignment.Center;
            king.VerticalAlignment = VerticalAlignment.Center;
            emblem.Child = king;
            grid.Children.Add(emblem);

            StackPanel titles = new StackPanel();
            titles.Margin = new Thickness(18, 0, 0, 0);
            TextBlock eyebrow = new TextBlock();
            eyebrow.Text = "GOVERNED APPLICATION INTELLIGENCE";
            eyebrow.FontSize = 10;
            eyebrow.FontWeight = FontWeights.SemiBold;
            eyebrow.Foreground = new SolidColorBrush(Color.FromRgb(126, 149, 188));
            titles.Children.Add(eyebrow);
            TextBlock product = new TextBlock();
            product.Text = "THEKEY";
            product.FontSize = 29;
            product.FontWeight = FontWeights.Bold;
            product.Foreground = Brushes.White;
            product.Margin = new Thickness(0, 1, 0, 0);
            titles.Children.Add(product);
            TextBlock name = new TextBlock();
            name.Text = "THE KING OF CHECKMATE";
            name.FontSize = 15;
            name.FontWeight = FontWeights.SemiBold;
            name.Foreground = new SolidColorBrush(Color.FromRgb(232, 190, 82));
            titles.Children.Add(name);
            Grid.SetColumn(titles, 1);
            grid.Children.Add(titles);

            Border trustBadge = new Border();
            trustBadge.Padding = new Thickness(14, 9, 14, 9);
            trustBadge.CornerRadius = new CornerRadius(18);
            trustBadge.Background = new SolidColorBrush(Color.FromArgb(82, 29, 51, 68));
            trustBadge.BorderBrush = new SolidColorBrush(Color.FromRgb(58, 92, 102));
            trustBadge.BorderThickness = new Thickness(1);
            trustBadge.VerticalAlignment = VerticalAlignment.Center;
            TextBlock trustText = new TextBlock();
            trustText.Text = "●  LOCAL · PRIVACY FIRST";
            trustText.FontSize = 10;
            trustText.FontWeight = FontWeights.SemiBold;
            trustText.Foreground = new SolidColorBrush(Color.FromRgb(116, 219, 172));
            trustBadge.Child = trustText;
            Grid.SetColumn(trustBadge, 2);
            grid.Children.Add(trustBadge);
            border.Child = grid;
            return border;
        }

        private Button CreateCard(string symbol, string title, string detail, RoutedEventHandler action)
        {
            Button button = new Button();
            button.Height = 180;
            button.Margin = new Thickness(6);
            button.Padding = new Thickness(18, 14, 18, 13);
            button.Background = new LinearGradientBrush(
                Color.FromRgb(13, 29, 48), Color.FromRgb(6, 17, 31), 90);
            button.BorderBrush = new SolidColorBrush(Color.FromRgb(68, 69, 70));
            button.BorderThickness = new Thickness(1);
            button.Foreground = Brushes.White;
            button.Cursor = Cursors.Hand;
            button.HorizontalContentAlignment = HorizontalAlignment.Stretch;
            button.Template = CreateCardTemplate();
            button.Effect = new DropShadowEffect
            {
                Color = Color.FromRgb(0, 0, 0),
                BlurRadius = 10,
                ShadowDepth = 3,
                Opacity = 0.2
            };
            button.ToolTip = title + " — " + detail;
            AutomationProperties.SetName(button, title);
            AutomationProperties.SetHelpText(button, detail);
            AttachHoverAnimation(button);
            button.Click += action;

            Grid content = new Grid();
            content.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            content.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            content.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            content.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            Border iconRing = new Border();
            iconRing.Width = 56;
            iconRing.Height = 56;
            iconRing.CornerRadius = new CornerRadius(28);
            iconRing.HorizontalAlignment = HorizontalAlignment.Left;
            iconRing.Background = new SolidColorBrush(Color.FromArgb(50, 210, 159, 50));
            iconRing.BorderBrush = new SolidColorBrush(Color.FromRgb(151, 111, 42));
            iconRing.BorderThickness = new Thickness(1);
            TextBlock icon = new TextBlock();
            icon.Text = symbol;
            icon.FontFamily = new FontFamily("Segoe UI Symbol");
            icon.FontSize = 28;
            icon.Foreground = new SolidColorBrush(Color.FromRgb(232, 190, 82));
            icon.HorizontalAlignment = HorizontalAlignment.Center;
            icon.VerticalAlignment = VerticalAlignment.Center;
            iconRing.Child = icon;
            content.Children.Add(iconRing);
            TextBlock heading = new TextBlock();
            heading.Text = title;
            heading.FontSize = 15;
            heading.FontWeight = FontWeights.SemiBold;
            heading.Foreground = Brushes.White;
            heading.TextWrapping = TextWrapping.Wrap;
            heading.Margin = new Thickness(0, 10, 0, 0);
            Grid.SetRow(heading, 1);
            content.Children.Add(heading);
            Border accent = new Border
            {
                Width = 18,
                Height = 2,
                Background = new SolidColorBrush(Color.FromRgb(224, 171, 60)),
                HorizontalAlignment = HorizontalAlignment.Left,
                Margin = new Thickness(0, 8, 0, 8)
            };
            Grid.SetRow(accent, 2);
            content.Children.Add(accent);
            Grid cardFooter = new Grid();
            cardFooter.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            cardFooter.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            TextBlock description = new TextBlock();
            description.Text = detail;
            description.FontSize = 10;
            description.Foreground = new SolidColorBrush(Color.FromRgb(161, 176, 204));
            description.TextWrapping = TextWrapping.Wrap;
            cardFooter.Children.Add(description);
            TextBlock arrow = new TextBlock
            {
                Text = "→",
                FontSize = 22,
                Foreground = new SolidColorBrush(Color.FromRgb(224, 228, 236)),
                HorizontalAlignment = HorizontalAlignment.Right,
                VerticalAlignment = VerticalAlignment.Bottom,
                Margin = new Thickness(8, 0, 0, 0)
            };
            Grid.SetColumn(arrow, 1);
            cardFooter.Children.Add(arrow);
            Grid.SetRow(cardFooter, 3);
            content.Children.Add(cardFooter);
            button.Content = content;
            return button;
        }

        private Button CreateFutureCard(string symbol, string title, string detail)
        {
            Button button = new Button();
            button.Height = 92;
            button.Margin = new Thickness(6, 2, 6, 2);
            button.Padding = new Thickness(16, 9, 16, 9);
            button.Background = new SolidColorBrush(Color.FromRgb(14, 23, 40));
            button.BorderBrush = new SolidColorBrush(Color.FromRgb(46, 61, 87));
            button.BorderThickness = new Thickness(1);
            button.HorizontalContentAlignment = HorizontalAlignment.Stretch;
            button.Template = CreateCardTemplate();
            button.IsEnabled = false;
            button.ToolTip = "Próximamente / Coming soon — " + detail;
            AutomationProperties.SetName(button, title + " — Próximamente / Coming soon");

            Grid content = new Grid();
            content.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(42) });
            content.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            content.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            TextBlock icon = new TextBlock();
            icon.Text = symbol;
            icon.FontFamily = new FontFamily("Segoe UI Symbol");
            icon.FontSize = 22;
            icon.Foreground = new SolidColorBrush(Color.FromRgb(184, 151, 70));
            icon.VerticalAlignment = VerticalAlignment.Center;
            content.Children.Add(icon);
            StackPanel copy = new StackPanel();
            copy.VerticalAlignment = VerticalAlignment.Center;
            TextBlock heading = new TextBlock();
            heading.Text = title;
            heading.FontSize = 14;
            heading.FontWeight = FontWeights.SemiBold;
            heading.Foreground = new SolidColorBrush(Color.FromRgb(222, 228, 240));
            copy.Children.Add(heading);
            TextBlock description = new TextBlock();
            description.Text = detail;
            description.FontSize = 10;
            description.Foreground = new SolidColorBrush(Color.FromRgb(133, 149, 178));
            copy.Children.Add(description);
            Grid.SetColumn(copy, 1);
            content.Children.Add(copy);
            Border badge = new Border();
            badge.Padding = new Thickness(8, 4, 8, 4);
            badge.CornerRadius = new CornerRadius(10);
            badge.Background = new SolidColorBrush(Color.FromRgb(28, 38, 59));
            TextBlock badgeText = new TextBlock();
            badgeText.Text = "PRÓXIMAMENTE / SOON";
            badgeText.FontSize = 9;
            badgeText.Foreground = new SolidColorBrush(Color.FromRgb(157, 171, 198));
            badge.Child = badgeText;
            Grid.SetColumn(badge, 2);
            content.Children.Add(badge);
            button.Content = content;
            return button;
        }

        private static void AttachHoverAnimation(Button button)
        {
            TranslateTransform transform = new TranslateTransform();
            button.RenderTransform = transform;
            button.RenderTransformOrigin = new Point(0.5, 0.5);
            button.MouseEnter += delegate
            {
                if (!button.IsEnabled) return;
                DoubleAnimation lift = new DoubleAnimation(-2, TimeSpan.FromMilliseconds(140));
                lift.EasingFunction = new QuadraticEase { EasingMode = EasingMode.EaseOut };
                transform.BeginAnimation(TranslateTransform.YProperty, lift);
            };
            button.MouseLeave += delegate
            {
                DoubleAnimation settle = new DoubleAnimation(0, TimeSpan.FromMilliseconds(170));
                settle.EasingFunction = new QuadraticEase { EasingMode = EasingMode.EaseOut };
                transform.BeginAnimation(TranslateTransform.YProperty, settle);
            };
        }

        private static ControlTemplate CreateCardTemplate()
        {
            ControlTemplate template = new ControlTemplate(typeof(Button));
            FrameworkElementFactory border = new FrameworkElementFactory(typeof(Border));
            border.SetValue(Border.CornerRadiusProperty, new CornerRadius(6));
            border.SetValue(Border.BackgroundProperty,
                new TemplateBindingExtension(Control.BackgroundProperty));
            border.SetValue(Border.BorderBrushProperty,
                new TemplateBindingExtension(Control.BorderBrushProperty));
            border.SetValue(Border.BorderThicknessProperty,
                new TemplateBindingExtension(Control.BorderThicknessProperty));

            FrameworkElementFactory presenter = new FrameworkElementFactory(typeof(ContentPresenter));
            presenter.SetValue(ContentPresenter.ContentProperty,
                new TemplateBindingExtension(ContentControl.ContentProperty));
            presenter.SetValue(ContentPresenter.HorizontalAlignmentProperty,
                new TemplateBindingExtension(Control.HorizontalContentAlignmentProperty));
            presenter.SetValue(ContentPresenter.VerticalAlignmentProperty,
                new TemplateBindingExtension(Control.VerticalContentAlignmentProperty));
            presenter.SetValue(FrameworkElement.MarginProperty,
                new TemplateBindingExtension(Control.PaddingProperty));
            border.AppendChild(presenter);
            template.VisualTree = border;

            Trigger hover = new Trigger();
            hover.Property = UIElement.IsMouseOverProperty;
            hover.Value = true;
            hover.Setters.Add(new Setter(
                Control.BackgroundProperty,
                new SolidColorBrush(Color.FromRgb(28, 43, 72))));
            hover.Setters.Add(new Setter(
                Control.BorderBrushProperty,
                new SolidColorBrush(Color.FromRgb(232, 190, 82))));
            template.Triggers.Add(hover);

            Trigger pressed = new Trigger();
            pressed.Property = Button.IsPressedProperty;
            pressed.Value = true;
            pressed.Setters.Add(new Setter(
                Control.BackgroundProperty,
                new SolidColorBrush(Color.FromRgb(12, 21, 39))));
            template.Triggers.Add(pressed);

            Trigger focused = new Trigger();
            focused.Property = UIElement.IsKeyboardFocusedProperty;
            focused.Value = true;
            focused.Setters.Add(new Setter(
                Control.BorderBrushProperty,
                new SolidColorBrush(Color.FromRgb(255, 215, 112))));
            focused.Setters.Add(new Setter(
                Control.BorderThicknessProperty,
                new Thickness(2)));
            template.Triggers.Add(focused);

            Trigger disabled = new Trigger();
            disabled.Property = UIElement.IsEnabledProperty;
            disabled.Value = false;
            disabled.Setters.Add(new Setter(
                Control.BackgroundProperty,
                new SolidColorBrush(Color.FromRgb(24, 35, 58))));
            disabled.Setters.Add(new Setter(
                Control.BorderBrushProperty,
                new SolidColorBrush(Color.FromRgb(82, 101, 130))));
            disabled.Setters.Add(new Setter(
                FrameworkElement.CursorProperty,
                Cursors.Arrow));
            template.Triggers.Add(disabled);

            return template;
        }

        private Button CreatePrimaryAction()
        {
            Button button = new Button();
            button.Height = 104;
            button.Margin = new Thickness(6, 0, 6, 2);
            button.Padding = new Thickness(24, 12, 24, 12);
            button.Background = new LinearGradientBrush(
                Color.FromRgb(245, 203, 92), Color.FromRgb(220, 166, 49), 0);
            button.BorderBrush = new SolidColorBrush(Color.FromRgb(255, 225, 142));
            button.BorderThickness = new Thickness(1);
            button.Foreground = new SolidColorBrush(Color.FromRgb(8, 13, 26));
            button.Cursor = Cursors.Hand;
            button.Template = CreatePrimaryTemplate();
            button.ToolTip = "Seleccionar y analizar una aplicación local / Select and analyze a local application";
            AutomationProperties.SetName(button, "Seleccionar y analizar / Select and analyze");
            AutomationProperties.SetHelpText(button, "Inspección local de solo lectura / Local read-only inspection");
            AttachHoverAnimation(button);
            button.Click += SelectApplication;

            StackPanel content = new StackPanel();
            content.HorizontalAlignment = HorizontalAlignment.Center;
            content.VerticalAlignment = VerticalAlignment.Center;
            TextBlock heading = new TextBlock();
            heading.Text = "\u25A3  SELECCIONAR Y ANALIZAR / SELECT & ANALYZE";
            heading.FontSize = 21;
            heading.FontWeight = FontWeights.Bold;
            heading.HorizontalAlignment = HorizontalAlignment.Center;
            content.Children.Add(heading);
            TextBlock description = new TextBlock();
            description.Text = "Aplicación local / Local application · solo lectura / read-only";
            description.FontSize = 13;
            description.Margin = new Thickness(0, 6, 0, 0);
            description.HorizontalAlignment = HorizontalAlignment.Center;
            content.Children.Add(description);
            button.Content = content;
            return button;
        }

        private static ControlTemplate CreatePrimaryTemplate()
        {
            ControlTemplate template = new ControlTemplate(typeof(Button));
            FrameworkElementFactory border = new FrameworkElementFactory(typeof(Border));
            border.SetValue(Border.CornerRadiusProperty, new CornerRadius(9));
            border.SetValue(Border.BackgroundProperty,
                new TemplateBindingExtension(Control.BackgroundProperty));
            border.SetValue(Border.BorderBrushProperty,
                new TemplateBindingExtension(Control.BorderBrushProperty));
            border.SetValue(Border.BorderThicknessProperty,
                new TemplateBindingExtension(Control.BorderThicknessProperty));
            border.SetValue(Border.EffectProperty, new DropShadowEffect
            {
                Color = Color.FromRgb(220, 166, 49),
                BlurRadius = 20,
                ShadowDepth = 4,
                Opacity = 0.2
            });
            FrameworkElementFactory presenter = new FrameworkElementFactory(typeof(ContentPresenter));
            presenter.SetValue(ContentPresenter.ContentProperty,
                new TemplateBindingExtension(ContentControl.ContentProperty));
            presenter.SetValue(ContentPresenter.HorizontalAlignmentProperty, HorizontalAlignment.Center);
            presenter.SetValue(ContentPresenter.VerticalAlignmentProperty, VerticalAlignment.Center);
            presenter.SetValue(FrameworkElement.MarginProperty,
                new TemplateBindingExtension(Control.PaddingProperty));
            border.AppendChild(presenter);
            template.VisualTree = border;

            Trigger hover = new Trigger();
            hover.Property = UIElement.IsMouseOverProperty;
            hover.Value = true;
            hover.Setters.Add(new Setter(
                Control.BackgroundProperty,
                new SolidColorBrush(Color.FromRgb(255, 215, 112))));
            template.Triggers.Add(hover);
            Trigger pressed = new Trigger();
            pressed.Property = Button.IsPressedProperty;
            pressed.Value = true;
            pressed.Setters.Add(new Setter(
                Control.BackgroundProperty,
                new SolidColorBrush(Color.FromRgb(207, 151, 36))));
            template.Triggers.Add(pressed);
            Trigger focused = new Trigger();
            focused.Property = UIElement.IsKeyboardFocusedProperty;
            focused.Value = true;
            focused.Setters.Add(new Setter(Control.BorderBrushProperty, Brushes.White));
            focused.Setters.Add(new Setter(Control.BorderThicknessProperty, new Thickness(2)));
            template.Triggers.Add(focused);
            return template;
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
            if (sourceState != null)
            {
                sourceState.Text = "✓  Aplicación / Application\n     " + Path.GetFileName(selectedProject);
                sourceState.Foreground = new SolidColorBrush(Color.FromRgb(91, 213, 126));
            }
            if (recentActivity != null)
            {
                recentTime.Text = DateTime.Now.ToString("HH:mm:ss");
                recentType.Text = "Análisis / Analysis";
                recentActivity.Text = Path.GetFileName(selectedProject);
                recentState.Text = "En curso / Running";
                recentState.Foreground = new SolidColorBrush(Color.FromRgb(216, 177, 83));
            }
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
            if (recentActivity != null)
            {
                recentTime.Text = DateTime.Now.ToString("HH:mm:ss");
                recentType.Text = arguments.Split(' ')[0].ToUpperInvariant();
                recentActivity.Text = runningStatus;
                recentState.Text = "En curso / Running";
                recentState.Foreground = new SolidColorBrush(Color.FromRgb(216, 177, 83));
            }
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
                    if (recentActivity != null)
                    {
                        recentTime.Text = DateTime.Now.ToString("HH:mm:ss");
                        recentType.Text = arguments.Split(' ')[0].ToUpperInvariant();
                        recentActivity.Text = "Exit " + exitCode + " · " + arguments;
                        recentState.Text = exitCode == 0 ? "Éxito / Success" : "Bloqueado / Blocked";
                        recentState.Foreground = new SolidColorBrush(
                            exitCode == 0 ? Color.FromRgb(91, 221, 126) : Color.FromRgb(255, 126, 126));
                    }
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
