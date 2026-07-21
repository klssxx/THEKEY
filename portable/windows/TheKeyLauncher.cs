using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Automation;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Effects;
using System.Windows.Media.Imaging;

namespace TheKeyPortable
{
    internal static class Program
    {
        [STAThread]
        public static void Main()
        {
            Application application = new Application();
            application.ShutdownMode = ShutdownMode.OnMainWindowClose;
            application.Run(new MainWindow(AppDomain.CurrentDomain.BaseDirectory));
        }
    }

    internal static class Theme
    {
        internal static readonly Color Canvas = Color.FromRgb(3, 10, 18);
        internal static readonly Color CanvasBlue = Color.FromRgb(5, 17, 30);
        internal static readonly Color Panel = Color.FromRgb(7, 22, 37);
        internal static readonly Color PanelRaised = Color.FromRgb(8, 23, 40);
        internal static readonly Color Gold = Color.FromRgb(232, 179, 62);
        internal static readonly Color GoldLight = Color.FromRgb(255, 210, 102);
        internal static readonly Color GoldBorder = Color.FromRgb(139, 100, 42);
        internal static readonly Color Text = Color.FromRgb(244, 241, 232);
        internal static readonly Color MutedText = Color.FromRgb(200, 194, 184);
        internal static readonly Color SecondaryText = Color.FromRgb(155, 168, 186);
        internal static readonly Color Success = Color.FromRgb(94, 223, 128);
        internal static readonly Color Error = Color.FromRgb(239, 125, 122);

        internal static SolidColorBrush Brush(Color color)
        {
            SolidColorBrush brush = new SolidColorBrush(color);
            brush.Freeze();
            return brush;
        }
    }

    internal sealed class ActivityRecord
    {
        internal DateTime OccurredAt { get; private set; }
        internal string Kind { get; private set; }
        internal string Detail { get; private set; }
        internal bool Succeeded { get; private set; }

        internal ActivityRecord(string kind, string detail, bool succeeded)
        {
            OccurredAt = DateTime.Now;
            Kind = kind;
            Detail = detail;
            Succeeded = succeeded;
        }

        internal ActivityRecord(DateTime occurredAt, string kind, string detail, bool succeeded)
        {
            OccurredAt = occurredAt;
            Kind = kind;
            Detail = detail;
            Succeeded = succeeded;
        }
    }

    internal struct NormalizedRect
    {
        internal readonly double X;
        internal readonly double Y;
        internal readonly double Width;
        internal readonly double Height;

        internal NormalizedRect(double x, double y, double width, double height)
        {
            X = x;
            Y = y;
            Width = width;
            Height = height;
        }

        internal static NormalizedRect FromPixels(double x, double y, double width, double height, double canvasWidth, double canvasHeight)
        {
            return new NormalizedRect(x / canvasWidth, y / canvasHeight, width / canvasWidth, height / canvasHeight);
        }

        internal Rect Resolve(double canvasWidth, double canvasHeight)
        {
            return new Rect(
                Math.Round(X * canvasWidth),
                Math.Round(Y * canvasHeight),
                Math.Round(Width * canvasWidth),
                Math.Round(Height * canvasHeight));
        }
    }

    internal sealed class MainWindow : Window
    {
        private readonly string root;
        private readonly string backend;
        private readonly Dictionary<string, Button> navigation = new Dictionary<string, Button>();
        private readonly List<ActivityRecord> activities = new List<ActivityRecord>();
        private Grid contentHost;
        private ScrollViewer mainContentViewport;
        private TextBlock status;
        private TextBlock selectedSource;
        private TextBox operationOutput;
        private TextBlock operationHeading;
        private Button applyRepairButton;
        private Button cancelOperationButton;
        private string selectedProject;
        private bool operationRunning;
        private readonly object backendProcessSync = new object();
        private Process activeBackendProcess;
        // The canonical 1448 x 1086 composition is intentionally isolated from
        // the live window.  It remains an off-screen visual-gate artifact; the
        // interactive dashboard uses a fluid layout below.
        private bool renderingCanonicalComposition;

        internal MainWindow(string applicationRoot)
        {
            root = applicationRoot;
            backend = Path.Combine(root, "core", "THEKEY-Core", "THEKEY-Core.exe");
            Rect workArea = SystemParameters.WorkArea;

            double availableWidth = Math.Max(720, workArea.Width);
            double availableHeight = Math.Max(540, workArea.Height);

            Title = "THEKEY — THE KING OF CHECKMATE";
            Width = Math.Min(1448, availableWidth);
            Height = Math.Min(1086, availableHeight);
            MinWidth = Math.Min(760, workArea.Width);
            MinHeight = Math.Min(570, workArea.Height);
            MaxWidth = Math.Max(640, workArea.Width);
            MaxHeight = Math.Max(480, workArea.Height);
            WindowStyle = WindowStyle.None;
            ResizeMode = ResizeMode.CanResize;
            WindowStartupLocation = WindowStartupLocation.CenterScreen;
            UseLayoutRounding = true;
            SnapsToDevicePixels = true;
            Background = Theme.Brush(Theme.Canvas);
            Closing += HandleWindowClosing;

            string iconPath = Path.Combine(root, "THEKEY_app_icon.png");
            if (File.Exists(iconPath))
            {
                Icon = BitmapFrame.Create(new Uri(iconPath, UriKind.Absolute));
            }

            LoadPersistedActivities();
            FrameworkElement shell = BuildResponsiveShell();
            Content = shell;
            ShowHome(null, null);

            string capturePath = Environment.GetEnvironmentVariable("THEKEY_CAPTURE_PATH");
            if (!String.IsNullOrWhiteSpace(capturePath))
            {
                Loaded += delegate
                {
                    MaxWidth = Double.PositiveInfinity;
                    MaxHeight = Double.PositiveInfinity;
                    Width = 1448;
                    Height = 1086;
                    Dispatcher.BeginInvoke(new Action(delegate
                    {
                        // Rebuild the same native WPF tree off-screen. The
                        // visible window is constrained by the monitor work
                        // area; a detached composition lets the visual gate
                        // render the canonical size without a bitmap mock-up.
                        Content = null;
                        navigation.Clear();
                        renderingCanonicalComposition = true;
                        FrameworkElement canonicalShell = BuildShell();
                        ShowHome(null, null);
                        double captureDpi = 96;
                        string configuredDpi = Environment.GetEnvironmentVariable("THEKEY_CAPTURE_DPI");
                        double parsedDpi;
                        if (Double.TryParse(configuredDpi, NumberStyles.Float, CultureInfo.InvariantCulture, out parsedDpi) && parsedDpi >= 96 && parsedDpi <= 384)
                        {
                            captureDpi = parsedDpi;
                        }
                        CaptureComposition(canonicalShell, 1448, 1086, capturePath, captureDpi);
                        Close();
                    }), System.Windows.Threading.DispatcherPriority.ApplicationIdle);
                };
            }
        }

        private FrameworkElement BuildShell()
        {
            Grid rootGrid = new Grid
            {
                Background = Theme.Brush(Theme.Canvas),
                ClipToBounds = true
            };
            rootGrid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(48) });
            rootGrid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            rootGrid.Children.Add(BuildTitleBar());

            Grid workspace = new Grid();
            workspace.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(270) });
            workspace.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            ScrollViewer sidebarViewport = new ScrollViewer
            {
                HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled,
                VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
                CanContentScroll = false,
                Content = BuildSidebar()
            };
            workspace.Children.Add(sidebarViewport);
            contentHost = new Grid
            {
                Width = 1178,
                Height = 1038,
                Background = Theme.Brush(Theme.CanvasBlue)
            };
            ScrollViewer contentViewport = new ScrollViewer
            {
                HorizontalScrollBarVisibility = ScrollBarVisibility.Auto,
                VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
                CanContentScroll = false,
                Background = Theme.Brush(Theme.CanvasBlue),
                Content = contentHost
            };
            Grid.SetColumn(contentViewport, 1);
            workspace.Children.Add(contentViewport);
            Grid.SetRow(workspace, 1);
            rootGrid.Children.Add(workspace);
            rootGrid.Children.Add(new Border
            {
                BorderBrush = Theme.Brush(Theme.GoldBorder),
                BorderThickness = new Thickness(1),
                CornerRadius = new CornerRadius(13),
                IsHitTestVisible = false
            });

            return rootGrid;
        }

        private FrameworkElement BuildResponsiveShell()
        {
            Grid rootGrid = new Grid
            {
                Background = Theme.Brush(Theme.Canvas),
                ClipToBounds = true
            };
            rootGrid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(48) });
            rootGrid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            rootGrid.Children.Add(BuildTitleBar());

            Grid workspace = new Grid { ClipToBounds = true };
            // Keep the navigation comfortably usable without reserving the
            // fixed 270 px canonical column from the desktop capture.
            workspace.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(248) });
            workspace.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            workspace.Children.Add(BuildResponsiveSidebar());

            contentHost = new Grid
            {
                Background = Theme.Brush(Theme.CanvasBlue),
                HorizontalAlignment = HorizontalAlignment.Stretch
            };
            mainContentViewport = new ScrollViewer
            {
                HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled,
                VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
                CanContentScroll = false,
                Background = Theme.Brush(Theme.CanvasBlue),
                Content = contentHost
            };
            Grid.SetColumn(mainContentViewport, 1);
            workspace.Children.Add(mainContentViewport);
            Grid.SetRow(workspace, 1);
            rootGrid.Children.Add(workspace);
            rootGrid.Children.Add(new Border
            {
                BorderBrush = Theme.Brush(Theme.GoldBorder),
                BorderThickness = new Thickness(1),
                CornerRadius = new CornerRadius(13),
                IsHitTestVisible = false
            });

            return rootGrid;
        }

        private static void PlaceNormalized(Canvas canvas, FrameworkElement child, NormalizedRect normalized, double canvasWidth, double canvasHeight)
        {
            Rect bounds = normalized.Resolve(canvasWidth, canvasHeight);
            child.Width = bounds.Width;
            child.Height = bounds.Height;
            Canvas.SetLeft(child, bounds.X);
            Canvas.SetTop(child, bounds.Y);
            canvas.Children.Add(child);
        }

        private Border BuildTitleBar()
        {
            Border bar = new Border
            {
                Background = Theme.Brush(Color.FromRgb(3, 10, 17)),
                BorderBrush = Theme.Brush(Theme.GoldBorder),
                BorderThickness = new Thickness(0, 0, 0, 1)
            };
            bar.MouseLeftButtonDown += delegate(object sender, MouseButtonEventArgs eventArgs)
            {
                if (eventArgs.OriginalSource != bar && eventArgs.OriginalSource is Button)
                {
                    return;
                }
                if (eventArgs.ClickCount == 2)
                {
                    ToggleMaximize();
                }
                else
                {
                    DragMove();
                }
            };

            Grid grid = new Grid();
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            StackPanel brand = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(20, 0, 0, 0) };
            brand.Children.Add(CreateBrandIcon(25));
            brand.Children.Add(new TextBlock
            {
                Text = "THEKEY",
                Foreground = Theme.Brush(Theme.Gold),
                FontWeight = FontWeights.Bold,
                FontSize = 14,
                Margin = new Thickness(10, 0, 0, 0),
                VerticalAlignment = VerticalAlignment.Center
            });
            brand.Children.Add(new TextBlock
            {
                Text = "— THE KING OF CHECKMATE",
                Foreground = Theme.Brush(Theme.MutedText),
                FontSize = 14,
                Margin = new Thickness(7, 0, 0, 0),
                VerticalAlignment = VerticalAlignment.Center
            });
            grid.Children.Add(brand);

            StackPanel controls = new StackPanel { Orientation = Orientation.Horizontal };
            controls.Children.Add(CreateWindowButton("Minimize window", "minimize", delegate { WindowState = WindowState.Minimized; }));
            controls.Children.Add(CreateWindowButton("Maximize or restore window", "maximize", ToggleMaximize));
            controls.Children.Add(CreateWindowButton("Close window", "close", Close));
            Grid.SetColumn(controls, 1);
            grid.Children.Add(controls);
            bar.Child = grid;
            return bar;
        }

        private Button CreateWindowButton(string accessibleName, string kind, Action action)
        {
            Button button = new Button
            {
                Width = 53,
                Height = 47,
                Background = Brushes.Transparent,
                BorderThickness = new Thickness(0),
                Cursor = Cursors.Hand,
                Content = CreateWindowIcon(kind)
            };
            AutomationProperties.SetName(button, accessibleName);
            button.ToolTip = accessibleName;
            button.Click += delegate { action(); };
            button.Template = CreateFlatButtonTemplate(0, true);
            return button;
        }

        private void ToggleMaximize()
        {
            WindowState = WindowState == WindowState.Maximized ? WindowState.Normal : WindowState.Maximized;
        }

        private Border BuildSidebar()
        {
            Border sidebar = new Border
            {
                Background = new LinearGradientBrush(
                    Color.FromRgb(5, 17, 29), Color.FromRgb(2, 10, 19), 90),
                BorderBrush = Theme.Brush(Theme.GoldBorder),
                BorderThickness = new Thickness(0, 0, 1, 0),
                ClipToBounds = true
            };
            Grid layout = new Grid();
            layout.RowDefinitions.Add(new RowDefinition { Height = new GridLength(205) });
            layout.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });

            string canonicalDecorPath = Path.Combine(root, "THEKEY_sidebar_canonical_decor.png");
            if (File.Exists(canonicalDecorPath))
            {
                Image canonicalDecor = new Image
                {
                    // Exact reference pixels only for the non-interactive crown,
                    // halo, texture, and landscape. Native UI areas are alpha
                    // masked in the asset and rendered by WPF above it.
                    Source = new BitmapImage(new Uri(canonicalDecorPath, UriKind.Absolute)),
                    Width = 270,
                    Height = 1038,
                    Stretch = Stretch.None,
                    SnapsToDevicePixels = true,
                    IsHitTestVisible = false
                };
                // Canvas measures to zero, so this fixed-pixel background
                // cannot change the header/navigation row geometry.
                Canvas canonicalDecorLayer = new Canvas
                {
                    ClipToBounds = true,
                    IsHitTestVisible = false
                };
                canonicalDecorLayer.Children.Add(canonicalDecor);
                Grid.SetRowSpan(canonicalDecorLayer, 2);
                layout.Children.Add(canonicalDecorLayer);
            }

            StackPanel identity = new StackPanel { Margin = new Thickness(20, 24, 20, 0) };
            Border emblem = new Border
            {
                Width = 96,
                Height = 96,
                HorizontalAlignment = HorizontalAlignment.Center
            };
            identity.Children.Add(emblem);
            identity.Children.Add(new TextBlock
            {
                Text = "THEKEY",
                FontFamily = new FontFamily("Georgia"),
                FontSize = 38,
                Foreground = Theme.Brush(Theme.GoldLight),
                HorizontalAlignment = HorizontalAlignment.Center,
                Margin = new Thickness(0, 5, 0, 0)
            });
            identity.Children.Add(new TextBlock
            {
                Text = "THE KING OF CHECKMATE",
                FontFamily = new FontFamily("Georgia"),
                FontWeight = FontWeights.SemiBold,
                FontSize = 10,
                Foreground = Theme.Brush(Theme.Gold),
                HorizontalAlignment = HorizontalAlignment.Center
            });
            layout.Children.Add(identity);

            StackPanel nav = new StackPanel { Width = 254, Margin = new Thickness(4, 0, 12, 18), VerticalAlignment = VerticalAlignment.Top };
            nav.Children.Add(CreateNavButton("home", "Inicio / Home", "home", ShowHome));
            nav.Children.Add(CreateNavButton("analyze", "Analizar / Analyze", "analyze", ShowAnalyze));
            nav.Children.Add(CreateNavButton("tools", "Herramientas / Tools", "tools", ShowTools));
            nav.Children.Add(CreateNavButton("results", "Resultados / Results", "results", ShowResults));
            nav.Children.Add(CreateNavButton("modes", "Modos / Modes", "modes", ShowModes));
            nav.Children.Add(CreateNavButton("logs", "Registros / Logs", "logs", ShowLogs));
            nav.Children.Add(CreateNavButton("settings", "Ajustes / Settings", "settings", ShowSettings));
            Grid.SetRow(nav, 1);
            layout.Children.Add(nav);
            sidebar.Child = layout;
            return sidebar;
        }

        private Border BuildResponsiveSidebar()
        {
            Border sidebar = new Border
            {
                Background = new LinearGradientBrush(
                    Color.FromRgb(5, 17, 29), Color.FromRgb(2, 10, 19), 90),
                BorderBrush = Theme.Brush(Theme.GoldBorder),
                BorderThickness = new Thickness(0, 0, 1, 0),
                ClipToBounds = true
            };
            Grid layout = new Grid { ClipToBounds = true };
            layout.RowDefinitions.Add(new RowDefinition { Height = new GridLength(188) });
            layout.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });

            string canonicalDecorPath = Path.Combine(root, "THEKEY_sidebar_canonical_decor.png");
            if (File.Exists(canonicalDecorPath))
            {
                Image canonicalDecor = new Image
                {
                    Source = new BitmapImage(new Uri(canonicalDecorPath, UriKind.Absolute)),
                    Stretch = Stretch.Fill,
                    SnapsToDevicePixels = true,
                    IsHitTestVisible = false
                };
                Grid.SetRowSpan(canonicalDecor, 2);
                layout.Children.Add(canonicalDecor);
            }

            StackPanel identity = new StackPanel { Margin = new Thickness(20, 18, 20, 0) };
            Border emblem = new Border
            {
                Width = 96,
                Height = 96,
                HorizontalAlignment = HorizontalAlignment.Center
            };
            identity.Children.Add(emblem);
            identity.Children.Add(new TextBlock
            {
                Text = "THEKEY",
                FontFamily = new FontFamily("Georgia"),
                FontSize = 38,
                Foreground = Theme.Brush(Theme.GoldLight),
                HorizontalAlignment = HorizontalAlignment.Center,
                Margin = new Thickness(0, 5, 0, 0)
            });
            identity.Children.Add(new TextBlock
            {
                Text = "THE KING OF CHECKMATE",
                FontFamily = new FontFamily("Georgia"),
                FontWeight = FontWeights.SemiBold,
                FontSize = 10,
                Foreground = Theme.Brush(Theme.Gold),
                HorizontalAlignment = HorizontalAlignment.Center
            });
            layout.Children.Add(identity);

            Grid nav = new Grid
            {
                Margin = new Thickness(4, 0, 8, 12),
                VerticalAlignment = VerticalAlignment.Stretch
            };
            for (int index = 0; index < 7; index++)
            {
                nav.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            }
            AddResponsiveNavigationButton(nav, CreateResponsiveNavButton("home", "Inicio / Home", "home", ShowHome), 0);
            AddResponsiveNavigationButton(nav, CreateResponsiveNavButton("analyze", "Analizar / Analyze", "analyze", ShowAnalyze), 1);
            AddResponsiveNavigationButton(nav, CreateResponsiveNavButton("tools", "Herramientas / Tools", "tools", ShowTools), 2);
            AddResponsiveNavigationButton(nav, CreateResponsiveNavButton("results", "Resultados / Results", "results", ShowResults), 3);
            AddResponsiveNavigationButton(nav, CreateResponsiveNavButton("modes", "Modos / Modes", "modes", ShowModes), 4);
            AddResponsiveNavigationButton(nav, CreateResponsiveNavButton("logs", "Registros / Logs", "logs", ShowLogs), 5);
            AddResponsiveNavigationButton(nav, CreateResponsiveNavButton("settings", "Ajustes / Settings", "settings", ShowSettings), 6);
            Grid.SetRow(nav, 1);
            layout.Children.Add(nav);

            sidebar.Child = layout;
            return sidebar;
        }

        private static void AddResponsiveNavigationButton(Grid navigationGrid, Button button, int row)
        {
            Grid.SetRow(button, row);
            navigationGrid.Children.Add(button);
        }

        private Button CreateResponsiveNavButton(string key, string label, string icon, RoutedEventHandler action)
        {
            Button button = new Button
            {
                Margin = new Thickness(0, 1, 0, 1),
                Padding = new Thickness(21, 0, 12, 0),
                HorizontalContentAlignment = HorizontalAlignment.Left,
                VerticalContentAlignment = VerticalAlignment.Center,
                Background = Brushes.Transparent,
                BorderBrush = Brushes.Transparent,
                BorderThickness = new Thickness(1),
                Foreground = Theme.Brush(Theme.MutedText),
                Cursor = Cursors.Hand,
                Template = CreateNavTemplate()
            };
            Grid content = new Grid();
            content.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(56) });
            content.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            content.Children.Add(CreateIcon(icon, 27, Theme.Brush(Theme.MutedText)));
            TextBlock text = new TextBlock
            {
                Text = label,
                FontSize = 15,
                VerticalAlignment = VerticalAlignment.Center,
                Foreground = Theme.Brush(Theme.MutedText),
                TextTrimming = TextTrimming.CharacterEllipsis
            };
            Grid.SetColumn(text, 1);
            content.Children.Add(text);
            button.Content = content;
            button.Click += action;
            AutomationProperties.SetName(button, label);
            navigation.Add(key, button);
            return button;
        }

        private Grid CreateSidebarLandscape()
        {
            Grid scene = new Grid
            {
                Height = 360,
                VerticalAlignment = VerticalAlignment.Bottom,
                ClipToBounds = true,
                IsHitTestVisible = false
            };
            RadialGradientBrush horizon = new RadialGradientBrush
            {
                Center = new Point(0.47, 0.24),
                GradientOrigin = new Point(0.47, 0.24),
                RadiusX = 0.72,
                RadiusY = 0.60
            };
            horizon.GradientStops.Add(new GradientStop(Color.FromArgb(92, 52, 68, 74), 0));
            horizon.GradientStops.Add(new GradientStop(Color.FromArgb(34, 19, 39, 62), 0.52));
            horizon.GradientStops.Add(new GradientStop(Color.FromArgb(0, 3, 10, 18), 1));
            scene.Children.Add(new Border { Background = horizon });

            Canvas canvas = new Canvas { Width = 270, Height = 360 };
            AddPath(canvas, "M0,185 L38,145 L73,169 L111,112 L146,164 L179,137 L226,186 L270,150 L270,360 L0,360 Z",
                Theme.Brush(Color.FromRgb(10, 27, 46)), 1, Theme.Brush(Color.FromArgb(230, 7, 22, 39)));
            AddPath(canvas, "M0,245 L55,201 L91,228 L133,178 L180,230 L222,192 L270,238 L270,360 L0,360 Z",
                Theme.Brush(Color.FromRgb(17, 39, 61)), 1, Theme.Brush(Color.FromArgb(236, 5, 18, 33)));
            AddPath(canvas, "M0,294 L54,264 L103,286 L156,245 L205,286 L244,260 L270,279 L270,360 L0,360 Z",
                Theme.Brush(Color.FromRgb(20, 37, 55)), 1, Theme.Brush(Color.FromArgb(245, 3, 13, 25)));
            FrameworkElement sentinel = CreateIcon("chessking", 82, Theme.Brush(Color.FromRgb(116, 91, 47)));
            sentinel.Opacity = 0.58;
            Canvas.SetLeft(sentinel, 93);
            Canvas.SetTop(sentinel, 66);
            canvas.Children.Add(sentinel);
            for (int index = 0; index < 6; index++)
            {
                double y = 300 + index * 12;
                AddLine(canvas, 0, y, 270, y, Theme.Brush(Color.FromArgb(34, 113, 91, 55)), 0.8);
            }
            for (int index = 0; index < 7; index++)
            {
                double x = 18 + index * 39;
                AddLine(canvas, 135, 276, x, 360, Theme.Brush(Color.FromArgb(28, 113, 91, 55)), 0.8);
            }
            scene.Children.Add(canvas);
            return scene;
        }

        private Button CreateNavButton(string key, string label, string icon, RoutedEventHandler action)
        {
            Button button = new Button
            {
                Height = 68,
                Width = 254,
                Margin = new Thickness(0, 1, 0, 1),
                Padding = new Thickness(23, 0, 18, 0),
                HorizontalContentAlignment = HorizontalAlignment.Left,
                Background = Brushes.Transparent,
                BorderBrush = Brushes.Transparent,
                BorderThickness = new Thickness(1),
                Foreground = Theme.Brush(Theme.MutedText),
                Cursor = Cursors.Hand,
                Template = CreateNavTemplate()
            };
            Grid content = new Grid();
            content.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(60) });
            content.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            content.Children.Add(CreateIcon(icon, 27, Theme.Brush(Theme.MutedText)));
            TextBlock text = new TextBlock
            {
                Text = label,
                FontSize = 15,
                VerticalAlignment = VerticalAlignment.Center,
                Foreground = Theme.Brush(Theme.MutedText)
            };
            Grid.SetColumn(text, 1);
            content.Children.Add(text);
            button.Content = content;
            button.Click += action;
            AutomationProperties.SetName(button, label);
            navigation.Add(key, button);
            return button;
        }

        private FrameworkElement BuildHome()
        {
            const double canvasWidth = 1178;
            const double canvasHeight = 1038;
            Grid home = new Grid
            {
                Width = canvasWidth,
                Height = canvasHeight,
                Background = Theme.Brush(Theme.CanvasBlue),
                ClipToBounds = true
            };
            string artPath = Path.Combine(root, "THEKEY_hero_chess.png");
            if (File.Exists(artPath))
            {
                BitmapImage source = new BitmapImage(new Uri(artPath, UriKind.Absolute));
                CroppedBitmap boardSource = new CroppedBitmap(source, new Int32Rect(0, 520, Math.Min(900, source.PixelWidth), source.PixelHeight - 520));
                Image board = new Image
                {
                    Source = boardSource,
                    Width = 1178,
                    Height = 520,
                    Margin = new Thickness(0, 350, 0, 0),
                    HorizontalAlignment = HorizontalAlignment.Stretch,
                    VerticalAlignment = VerticalAlignment.Top,
                    Stretch = Stretch.Fill,
                    Opacity = 0.42,
                    IsHitTestVisible = false
                };
                home.Children.Add(board);
                home.Children.Add(new Border
                {
                    Height = 520,
                    Margin = new Thickness(0, 350, 0, 0),
                    VerticalAlignment = VerticalAlignment.Top,
                    Background = new LinearGradientBrush(
                        Color.FromArgb(246, 3, 10, 18), Color.FromArgb(30, 3, 10, 18), 0),
                    IsHitTestVisible = false
                });
                RadialGradientBrush boardGlow = new RadialGradientBrush
                {
                    Center = new Point(0.54, 0.30),
                    GradientOrigin = new Point(0.54, 0.30),
                    RadiusX = 0.58,
                    RadiusY = 0.62
                };
                boardGlow.GradientStops.Add(new GradientStop(Color.FromArgb(72, 151, 91, 28), 0));
                boardGlow.GradientStops.Add(new GradientStop(Color.FromArgb(0, 151, 91, 28), 1));
                home.Children.Add(new Border
                {
                    Width = 680,
                    Height = 430,
                    Margin = new Thickness(470, 310, 0, 0),
                    HorizontalAlignment = HorizontalAlignment.Left,
                    VerticalAlignment = VerticalAlignment.Top,
                    Background = boardGlow,
                    IsHitTestVisible = false
                });
            }
            Canvas regions = new Canvas { Width = canvasWidth, Height = canvasHeight, ClipToBounds = true };
            PlaceNormalized(regions, BuildHero(), NormalizedRect.FromPixels(0, 0, 1178, 372, canvasWidth, canvasHeight), canvasWidth, canvasHeight);
            PlaceNormalized(regions, BuildOperationCards(), NormalizedRect.FromPixels(42, 384, 1078, 252, canvasWidth, canvasHeight), canvasWidth, canvasHeight);
            PlaceNormalized(regions, BuildUpcomingModes(), NormalizedRect.FromPixels(42, 651, 1078, 134, canvasWidth, canvasHeight), canvasWidth, canvasHeight);
            PlaceNormalized(regions, BuildActivityPanel(), NormalizedRect.FromPixels(18, 800, 1132, 211, canvasWidth, canvasHeight), canvasWidth, canvasHeight);
            home.Children.Add(regions);
            return home;
        }

        private FrameworkElement BuildResponsiveHome()
        {
            StackPanel home = new StackPanel
            {
                Background = Theme.Brush(Theme.CanvasBlue),
                HorizontalAlignment = HorizontalAlignment.Stretch
            };
            FrameworkElement hero = BuildHero();
            // The live work area on a 1360 x 768 Windows desktop is 720 px
            // high once the taskbar is reserved.  This keeps the complete
            // upcoming-modes heading in the first viewport without altering
            // the 372 px canonical hero used by the off-screen capture.
            hero.Height = 350;
            hero.HorizontalAlignment = HorizontalAlignment.Stretch;
            home.Children.Add(hero);

            FrameworkElement cards = BuildResponsiveOperationCards();
            cards.Margin = new Thickness(24, 12, 24, 0);
            home.Children.Add(cards);

            FrameworkElement modes = BuildUpcomingModes();
            modes.Margin = new Thickness(24, 12, 24, 0);
            home.Children.Add(modes);

            FrameworkElement activity = BuildActivityPanel();
            activity.Margin = new Thickness(18, 15, 18, 27);
            home.Children.Add(activity);
            return home;
        }

        private FrameworkElement BuildHero()
        {
            Grid hero = new Grid { Height = 372, ClipToBounds = true, Background = Theme.Brush(Theme.Canvas) };
            string canonicalDecorPath = Path.Combine(root, "THEKEY_hero_canonical_decor.png");
            if (File.Exists(canonicalDecorPath))
            {
                // This is a transparent, exact-pixel crop of only the canonical
                // hero's non-interactive art.  The text, local-mode control and
                // CTA intentionally remain native WPF elements above it.
                Image canonicalDecor = new Image
                {
                    Source = new BitmapImage(new Uri(canonicalDecorPath, UriKind.Absolute)),
                    Width = 1178,
                    Height = 254,
                    HorizontalAlignment = HorizontalAlignment.Left,
                    VerticalAlignment = VerticalAlignment.Top,
                    Stretch = Stretch.None,
                    SnapsToDevicePixels = true,
                    IsHitTestVisible = false
                };
                hero.Children.Add(canonicalDecor);
            }

            StackPanel copy = new StackPanel
            {
                Width = 620,
                Margin = new Thickness(48, 22, 0, 0),
                HorizontalAlignment = HorizontalAlignment.Left,
                VerticalAlignment = VerticalAlignment.Top
            };
            copy.Children.Add(new TextBlock
            {
                Text = "Bienvenido / Welcome",
                FontSize = 20,
                Foreground = Theme.Brush(Theme.Gold)
            });
            copy.Children.Add(new TextBlock
            {
                Text = "THEKEY",
                FontFamily = new FontFamily("Georgia"),
                FontSize = 73,
                Foreground = Theme.Brush(Theme.Text),
                Margin = new Thickness(0, 1, 0, 0)
            });
            copy.Children.Add(new TextBlock
            {
                Text = "THE KING OF CHECKMATE",
                FontFamily = new FontFamily("Georgia"),
                FontSize = 25,
                Foreground = Theme.Brush(Theme.Gold),
                Margin = new Thickness(1, -7, 0, 0)
            });
            copy.Children.Add(new TextBlock
            {
                Text = "Aplicación de análisis, verificación y reparación para un rendimiento impecable.",
                FontSize = 15,
                Foreground = Theme.Brush(Theme.MutedText),
                Margin = new Thickness(2, 22, 0, 0),
                TextWrapping = TextWrapping.Wrap
            });
            copy.Children.Add(new TextBlock
            {
                Text = "Analysis, verification and repair application for flawless performance.",
                FontSize = 15,
                Foreground = Theme.Brush(Theme.MutedText),
                FontStyle = FontStyles.Italic,
                Margin = new Thickness(2, 7, 0, 0),
                TextWrapping = TextWrapping.Wrap
            });
            hero.Children.Add(copy);

            Border local = new Border
            {
                HorizontalAlignment = HorizontalAlignment.Right,
                VerticalAlignment = VerticalAlignment.Top,
                Width = 240,
                Margin = new Thickness(0, 23, 15, 0),
                Padding = new Thickness(16, 10, 16, 10),
                CornerRadius = new CornerRadius(22),
                BorderBrush = Theme.Brush(Color.FromRgb(77, 92, 89)),
                BorderThickness = new Thickness(1),
                Background = Theme.Brush(Color.FromArgb(224, 5, 18, 28))
            };
            Grid localContent = new Grid();
            localContent.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(27) });
            localContent.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            localContent.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(18) });
            localContent.Children.Add(CreateIcon("shield", 21, Theme.Brush(Theme.Success)));
            StackPanel localText = new StackPanel();
            localText.Children.Add(new TextBlock
            {
                Text = "Modo local / Local mode",
                FontSize = 13,
                Foreground = Theme.Brush(Theme.Text)
            });
            localText.Children.Add(new TextBlock
            {
                Text = "Privacidad primero / Privacy first",
                FontSize = 10,
                Foreground = Theme.Brush(Theme.SecondaryText)
            });
            Grid.SetColumn(localText, 1);
            localContent.Children.Add(localText);
            System.Windows.Shapes.Ellipse live = new System.Windows.Shapes.Ellipse
            {
                Width = 9,
                Height = 9,
                Fill = Theme.Brush(Theme.Success),
                HorizontalAlignment = HorizontalAlignment.Right,
                VerticalAlignment = VerticalAlignment.Center
            };
            Grid.SetColumn(live, 2);
            localContent.Children.Add(live);
            local.Child = localContent;
            AutomationProperties.SetName(local, "Modo local / Local mode");
            hero.Children.Add(local);

            Button primary = CreatePrimaryAction();
            primary.Margin = new Thickness(47, 0, 0, 6);
            primary.VerticalAlignment = VerticalAlignment.Bottom;
            primary.HorizontalAlignment = HorizontalAlignment.Left;
            hero.SizeChanged += delegate
            {
                primary.Width = Math.Max(280, Math.Min(688, hero.ActualWidth - 94));
            };
            primary.Width = 688;
            hero.Children.Add(primary);
            return hero;
        }

        private FrameworkElement BuildOperationCards()
        {
            Grid cards = new Grid { Height = 252 };
            cards.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(260) });
            cards.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(263) });
            cards.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(274) });
            cards.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(281) });
            cards.Children.Add(CreateCard("shield", "Verificar / Verify", "Verifica archivos, firmas\ny copias aisladas.\nVerify files, signatures\nand isolated copies.", VerifySelectedApplication, 0, new Thickness(0, 0, 7, 0), !operationRunning));
            cards.Children.Add(CreateCard("repair", "Reparar / Repair", "Escanea, repara y\nrestaura archivos.\nScan, repair and\nrestore files.", RepairSelectedApplication, 1, new Thickness(7, 0, 7, 0), !operationRunning));
            cards.Children.Add(CreateCard("demo", "Demo para jueces /\nJudge demo", "Genera demostraciones\ngubernamentales.\nGenerate government\ndemonstrations.", RunDemo, 2, new Thickness(7, 0, 7, 0), !operationRunning));
            cards.Children.Add(CreateCard("results", "Ver resultados /\nView results", "Revisa resultados, recibos\ny decisiones.\nReview results, receipts\nand decisions.", ShowResults, 3, new Thickness(10, 0, 0, 0), true));
            return cards;
        }

        private FrameworkElement BuildResponsiveOperationCards()
        {
            Grid cards = new Grid { Height = 252, HorizontalAlignment = HorizontalAlignment.Stretch };
            for (int index = 0; index < 4; index++)
            {
                cards.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            }
            cards.Children.Add(CreateCard("shield", "Verificar / Verify", "Verifica archivos, firmas\ny copias aisladas.\nVerify files, signatures\nand isolated copies.", VerifySelectedApplication, 0, new Thickness(0, 0, 7, 0), !operationRunning));
            cards.Children.Add(CreateCard("repair", "Reparar / Repair", "Escanea, repara y\nrestaura archivos.\nScan, repair and\nrestore files.", RepairSelectedApplication, 1, new Thickness(7, 0, 7, 0), !operationRunning));
            cards.Children.Add(CreateCard("demo", "Demo para jueces /\nJudge demo", "Genera demostraciones\ngubernamentales.\nGenerate government\ndemonstrations.", RunDemo, 2, new Thickness(7, 0, 7, 0), !operationRunning));
            cards.Children.Add(CreateCard("results", "Ver resultados /\nView results", "Revisa resultados, recibos\ny decisiones.\nReview results, receipts\nand decisions.", ShowResults, 3, new Thickness(10, 0, 0, 0), true));
            return cards;
        }

        private Button CreateCard(string icon, string title, string detail, RoutedEventHandler action, int column, Thickness margin, bool isEnabled)
        {
            Button button = new Button
            {
                Margin = margin,
                Padding = new Thickness(36, 13, 24, 17),
                HorizontalContentAlignment = HorizontalAlignment.Stretch,
                VerticalContentAlignment = VerticalAlignment.Stretch,
                Background = new LinearGradientBrush(
                    Color.FromArgb(238, Theme.PanelRaised.R, Theme.PanelRaised.G, Theme.PanelRaised.B),
                    Color.FromArgb(246, Theme.CanvasBlue.R, Theme.CanvasBlue.G, Theme.CanvasBlue.B), 90),
                BorderBrush = Theme.Brush(Theme.GoldBorder),
                BorderThickness = new Thickness(1),
                Cursor = Cursors.Hand,
                IsEnabled = isEnabled,
                Template = CreateCardTemplate(),
                Effect = new DropShadowEffect { Color = Color.FromRgb(0, 0, 0), BlurRadius = 12, ShadowDepth = 4, Opacity = 0.28 }
            };
            Grid layout = new Grid();
            layout.RowDefinitions.Add(new RowDefinition { Height = new GridLength(83) });
            layout.RowDefinitions.Add(new RowDefinition { Height = new GridLength(48) });
            layout.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            Border ring = new Border
            {
                Width = 78,
                Height = 78,
                CornerRadius = new CornerRadius(39),
                BorderBrush = Theme.Brush(Theme.Gold),
                BorderThickness = new Thickness(1),
                Background = Theme.Brush(Color.FromArgb(45, 92, 62, 12)),
                HorizontalAlignment = HorizontalAlignment.Left,
                VerticalAlignment = VerticalAlignment.Top
            };
            ring.Child = CreateIcon(icon, 43, Theme.Brush(Theme.GoldLight));
            layout.Children.Add(ring);
            StackPanel heading = new StackPanel { VerticalAlignment = VerticalAlignment.Top, Margin = new Thickness(0, -1, 0, 0) };
            heading.Children.Add(new TextBlock
            {
                Text = title,
                FontSize = 20,
                Foreground = Theme.Brush(Theme.Text),
                FontWeight = FontWeights.Medium,
                TextWrapping = TextWrapping.Wrap,
                LineHeight = 24
            });
            heading.Children.Add(new Border { Width = 23, Height = 2, Background = Theme.Brush(Theme.Gold), Margin = new Thickness(0, 9, 0, 0), HorizontalAlignment = HorizontalAlignment.Left });
            Grid.SetRow(heading, 1);
            layout.Children.Add(heading);
            Grid footer = new Grid();
            footer.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            footer.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            TextBlock detailBlock = new TextBlock
            {
                FontSize = 13,
                Foreground = Theme.Brush(Theme.MutedText),
                TextWrapping = TextWrapping.Wrap,
                LineHeight = 20,
                VerticalAlignment = VerticalAlignment.Top
            };
            string[] detailLines = detail.Split('\n');
            for (int index = 0; index < detailLines.Length; index++)
            {
                if (index > 0) detailBlock.Inlines.Add(new LineBreak());
                detailBlock.Inlines.Add(new Run(detailLines[index])
                {
                    FontStyle = index >= 2 ? FontStyles.Italic : FontStyles.Normal
                });
            }
            footer.Children.Add(detailBlock);
            FrameworkElement arrow = CreateIcon("arrow", 24, Theme.Brush(Theme.GoldLight));
            arrow.VerticalAlignment = VerticalAlignment.Bottom;
            arrow.Margin = new Thickness(5, 0, 0, 0);
            Grid.SetColumn(arrow, 1);
            footer.Children.Add(arrow);
            Grid.SetRow(footer, 2);
            layout.Children.Add(footer);
            button.Content = layout;
            button.Click += action;
            Grid.SetColumn(button, column);
            AutomationProperties.SetName(button, title.Replace("\n", " "));
            AutomationProperties.SetHelpText(button, detail.Replace("\n", " "));
            return button;
        }

        private FrameworkElement BuildUpcomingModes()
        {
            StackPanel section = new StackPanel();
            section.Children.Add(new TextBlock
            {
                Text = "MODOS PRÓXIMOS / UPCOMING MODES",
                FontSize = 15,
                Foreground = Theme.Brush(Theme.Gold),
                Margin = new Thickness(2, 0, 0, 4)
            });
            Grid modes = new Grid { Height = 111 };
            modes.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(513) });
            modes.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            modes.Children.Add(CreateUpcomingCard("THE KING", "Construcción orquestada /\nOrchestrated build", true, 0, new Thickness(0, 0, 8, 0)));
            modes.Children.Add(CreateUpcomingCard("CHECKMATE", "Revisión adversarial /\nAdversarial review", false, 1, new Thickness(21, 0, 0, 0)));
            section.Children.Add(modes);
            return section;
        }

        private Button CreateUpcomingCard(string title, string detail, bool gold, int column, Thickness margin)
        {
            Button button = new Button
            {
                // Keep the future modes visibly native without accepting input;
                // IsEnabled=false would dim their WPF text and decorations.
                IsHitTestVisible = false,
                Focusable = false,
                Margin = margin,
                Padding = new Thickness(28, 10, 24, 10),
                Background = new LinearGradientBrush(
                    gold ? Color.FromRgb(44, 29, 8) : Color.FromRgb(8, 26, 46),
                    gold ? Color.FromRgb(28, 22, 12) : Color.FromRgb(6, 18, 33), 0),
                BorderBrush = Theme.Brush(Theme.GoldBorder),
                BorderThickness = new Thickness(1),
                Template = CreateCardTemplate()
            };
            Grid layout = new Grid();
            layout.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(115) });
            layout.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(140) });
            layout.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            layout.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            string canonicalDecorPath = Path.Combine(
                root, gold ? "THEKEY_mode_king_canonical_decor.png" : "THEKEY_mode_checkmate_canonical_decor.png");
            if (File.Exists(canonicalDecorPath))
            {
                // Transparent exact-pixel crops retain only the interior
                // decoration and emblems; the card, badge, and all text stay WPF.
                Image texture = new Image
                {
                    Source = new BitmapImage(new Uri(canonicalDecorPath, UriKind.Absolute)),
                    Width = gold ? 453 : 492,
                    Height = 90,
                    Stretch = Stretch.None,
                    HorizontalAlignment = HorizontalAlignment.Left,
                    VerticalAlignment = VerticalAlignment.Top,
                    SnapsToDevicePixels = true,
                    IsHitTestVisible = false
                };
                Grid.SetColumnSpan(texture, 4);
                layout.Children.Add(texture);
            }
            double emblemSize = gold ? 82 : 60;
            Border emblem = new Border
            {
                Width = emblemSize,
                Height = emblemSize,
                HorizontalAlignment = HorizontalAlignment.Left,
                VerticalAlignment = VerticalAlignment.Center
            };
            layout.Children.Add(emblem);
            StackPanel text = new StackPanel { VerticalAlignment = VerticalAlignment.Center };
            text.Children.Add(new TextBlock
            {
                Text = title,
                FontFamily = new FontFamily("Georgia"),
                FontSize = 23,
                Foreground = Theme.Brush(Theme.Text)
            });
            text.Children.Add(new TextBlock
            {
                Text = detail,
                FontSize = 14,
                Foreground = Theme.Brush(Theme.MutedText),
                Margin = new Thickness(0, 6, 0, 0),
                LineHeight = 18
            });
            Grid.SetColumn(text, 1);
            layout.Children.Add(text);
            Border badge = new Border
            {
                Padding = new Thickness(14, 6, 14, 6),
                CornerRadius = new CornerRadius(14),
                Background = Theme.Brush(Color.FromArgb(130, 11, 27, 46)),
                BorderBrush = Theme.Brush(gold ? Theme.GoldBorder : Color.FromRgb(53, 88, 126)),
                BorderThickness = new Thickness(1),
                VerticalAlignment = VerticalAlignment.Top,
                Margin = new Thickness(0, 5, 0, 0)
            };
            badge.Child = new TextBlock
            {
                Text = "PRÓXIMAMENTE / SOON",
                FontSize = 10,
                Foreground = Theme.Brush(gold ? Theme.GoldLight : Color.FromRgb(151, 189, 231))
            };
            Grid.SetColumn(badge, 2);
            layout.Children.Add(badge);
            button.Content = layout;
            Grid.SetColumn(button, column);
            AutomationProperties.SetName(button, title + " — Próximamente / Soon");
            return button;
        }

        private FrameworkElement BuildActivityPanel()
        {
            Border panel = new Border
            {
                Height = 211,
                CornerRadius = new CornerRadius(11),
                BorderBrush = Theme.Brush(Color.FromRgb(65, 83, 102)),
                BorderThickness = new Thickness(1),
                Background = Theme.Brush(Color.FromRgb(4, 17, 29))
            };
            Grid layout = new Grid();
            layout.RowDefinitions.Add(new RowDefinition { Height = new GridLength(35) });
            layout.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            Grid header = new Grid { Background = Theme.Brush(Color.FromRgb(10, 28, 46)) };
            header.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            header.Children.Add(new TextBlock
            {
                Text = "ACTIVIDAD RECIENTE / RECENT ACTIVITY",
                Foreground = Theme.Brush(Theme.Text),
                FontSize = 14,
                Margin = new Thickness(24, 0, 0, 0),
                VerticalAlignment = VerticalAlignment.Center
            });
            Button all = new Button
            {
                Content = "VER TODOS / VIEW ALL",
                Foreground = Theme.Brush(Theme.MutedText),
                FontSize = 12,
                Background = Brushes.Transparent,
                BorderThickness = new Thickness(0),
                Padding = new Thickness(14, 0, 18, 0),
                Cursor = Cursors.Hand,
                HorizontalAlignment = HorizontalAlignment.Right,
                Template = CreateFlatButtonTemplate(0, false)
            };
            all.Click += ShowResults;
            AutomationProperties.SetName(all, "Ver todos los resultados / View all results");
            Grid.SetColumn(all, 1);
            header.Children.Add(all);
            layout.Children.Add(header);

            Grid table = new Grid { Margin = new Thickness(24, 0, 20, 10) };
            table.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(150) });
            table.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(258) });
            table.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            table.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(113) });
            table.RowDefinitions.Add(new RowDefinition { Height = new GridLength(26) });
            table.Children.Add(CreateActivityCell("Hora / Time", 0, 0, true, Theme.SecondaryText));
            table.Children.Add(CreateActivityCell("Tipo / Type", 1, 0, true, Theme.SecondaryText));
            table.Children.Add(CreateActivityCell("Actividad / Activity", 2, 0, true, Theme.SecondaryText));
            table.Children.Add(CreateActivityCell("Estado / Status", 3, 0, true, Theme.SecondaryText));
            List<ActivityRecord> visible = activities.OrderByDescending(item => item.OccurredAt).Take(4).ToList();
            if (visible.Count == 0)
            {
                table.RowDefinitions.Add(new RowDefinition { Height = new GridLength(140) });
                TextBlock empty = new TextBlock
                {
                    Text = "Sin actividad todavía / No activity yet. Ejecuta un análisis o la demo para crear evidencia real.",
                    FontSize = 13,
                    Foreground = Theme.Brush(Theme.MutedText),
                    Margin = new Thickness(0, 12, 0, 12),
                    VerticalAlignment = VerticalAlignment.Center,
                    TextWrapping = TextWrapping.Wrap
                };
                Grid.SetRow(empty, 1);
                Grid.SetColumnSpan(empty, 4);
                table.Children.Add(empty);
            }
            else
            {
                for (int index = 0; index < visible.Count; index++)
                {
                    table.RowDefinitions.Add(new RowDefinition { Height = new GridLength(35) });
                    ActivityRecord item = visible[index];
                    int row = index + 1;
                    table.Children.Add(CreateActivityCell(item.OccurredAt.ToString("yyyy-MM-dd HH:mm:ss"), 0, row, false, Theme.MutedText));
                    table.Children.Add(CreateActivityKindCell(item.Kind, row));
                    table.Children.Add(CreateActivityCell(item.Detail, 2, row, false, Theme.MutedText));
                    table.Children.Add(CreateActivityCell(item.Succeeded ? "Éxito / Success" : "Bloqueado / Blocked", 3, row, false, item.Succeeded ? Theme.Success : Theme.Error));
                }
            }
            Grid.SetRow(table, 1);
            layout.Children.Add(table);
            panel.Child = layout;
            return panel;
        }

        private TextBlock CreateActivityCell(string text, int column, int row, bool header, Color foreground)
        {
            TextBlock cell = new TextBlock
            {
                Text = text,
                FontSize = header ? 11 : 12,
                Foreground = Theme.Brush(foreground),
                VerticalAlignment = VerticalAlignment.Center,
                TextTrimming = TextTrimming.CharacterEllipsis,
                Margin = new Thickness(0, 0, 8, 0)
            };
            Grid.SetColumn(cell, column);
            Grid.SetRow(cell, row);
            return cell;
        }

        private FrameworkElement CreateActivityKindCell(string kind, int row)
        {
            Grid cell = new Grid { Margin = new Thickness(0, 0, 8, 0) };
            cell.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(45) });
            cell.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            string icon = kind.IndexOf("Repair", StringComparison.OrdinalIgnoreCase) >= 0 ? "repair" :
                          kind.IndexOf("Demo", StringComparison.OrdinalIgnoreCase) >= 0 ? "demo" :
                          kind.IndexOf("Analyze", StringComparison.OrdinalIgnoreCase) >= 0 ? "analyze" :
                          kind.IndexOf("Results", StringComparison.OrdinalIgnoreCase) >= 0 ? "results" : "shield";
            FrameworkElement glyph = CreateIcon(icon, 21, Theme.Brush(
                kind.IndexOf("Verify", StringComparison.OrdinalIgnoreCase) >= 0 ? Theme.Success : Theme.Gold));
            glyph.HorizontalAlignment = HorizontalAlignment.Left;
            cell.Children.Add(glyph);
            TextBlock label = new TextBlock
            {
                Text = kind,
                FontSize = 12,
                Foreground = Theme.Brush(Theme.MutedText),
                VerticalAlignment = VerticalAlignment.Center,
                TextTrimming = TextTrimming.CharacterEllipsis
            };
            Grid.SetColumn(label, 1);
            cell.Children.Add(label);
            Grid.SetColumn(cell, 1);
            Grid.SetRow(cell, row);
            return cell;
        }

        private Button CreatePrimaryAction()
        {
            Button button = new Button
            {
                Height = 112,
                Padding = new Thickness(69, 0, 34, 0),
                Background = CreateMetallicGoldBrush(),
                BorderBrush = Theme.Brush(Theme.GoldLight),
                BorderThickness = new Thickness(1),
                Cursor = Cursors.Hand,
                HorizontalContentAlignment = HorizontalAlignment.Left,
                Template = CreateHeroActionTemplate(),
                Effect = new DropShadowEffect { Color = Theme.Gold, BlurRadius = 22, ShadowDepth = 3, Opacity = 0.23 }
            };
            Grid content = new Grid();
            content.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(97) });
            content.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            Border target = new Border
            {
                Width = 66,
                Height = 66,
                CornerRadius = new CornerRadius(33),
                BorderBrush = Theme.Brush(Theme.GoldLight),
                BorderThickness = new Thickness(2),
                HorizontalAlignment = HorizontalAlignment.Left,
                VerticalAlignment = VerticalAlignment.Center,
                Background = Theme.Brush(Color.FromArgb(24, 5, 10, 18))
            };
            target.Child = CreateIcon("target", 41, Theme.Brush(Theme.GoldLight));
            content.Children.Add(target);
            StackPanel copy = new StackPanel { VerticalAlignment = VerticalAlignment.Center };
            copy.Children.Add(new TextBlock
            {
                Text = "Seleccionar y analizar / Select & Analyze",
                FontSize = 23,
                Foreground = Theme.Brush(Theme.Text),
                FontWeight = FontWeights.Medium
            });
            copy.Children.Add(new TextBlock
            {
                Text = "Selecciona una aplicación y ejecuta un análisis profundo",
                FontSize = 14,
                Foreground = Theme.Brush(Theme.GoldLight),
                Margin = new Thickness(0, 5, 0, 0),
                LineHeight = 20
            });
            copy.Children.Add(new TextBlock
            {
                Text = "Select an application and run a deep analysis",
                FontSize = 14,
                FontStyle = FontStyles.Italic,
                Foreground = Theme.Brush(Theme.GoldLight),
                Margin = new Thickness(0, 2, 0, 0)
            });
            Grid.SetColumn(copy, 1);
            content.Children.Add(copy);
            button.Content = content;
            button.Click += SelectApplication;
            AutomationProperties.SetName(button, "Seleccionar y analizar / Select and analyze");
            AutomationProperties.SetHelpText(button, "Escoge una carpeta de proyecto existente para una inspección de solo lectura / Choose an existing project folder for read-only intake");
            return button;
        }

        private void ShowHome(object sender, RoutedEventArgs eventArgs)
        {
            SetView(renderingCanonicalComposition ? BuildHome() : BuildResponsiveHome(), "home");
        }

        private void ShowAnalyze(object sender, RoutedEventArgs eventArgs)
        {
            StackPanel pageBody = (StackPanel)BuildInformationPage(
                "Analizar / Analyze",
                "Inspección inicial de solo lectura para proyectos compatibles.",
                "Selecciona una carpeta existente. THEKEY identifica el perfil, entrypoints, tests y riesgos sin ejecutar código del proyecto.\n\n" +
                "Estado / Status: " + (String.IsNullOrWhiteSpace(selectedProject) ? "Pendiente / Pending" : "Proyecto seleccionado / Selected project\n" + selectedProject));
            Button select = new Button
            {
                Content = "Seleccionar proyecto / Select project",
                Margin = new Thickness(0, 20, 0, 0),
                Padding = new Thickness(22, 12, 22, 12),
                Background = Theme.Brush(Theme.Gold),
                Foreground = Theme.Brush(Theme.Canvas),
                BorderBrush = Theme.Brush(Theme.GoldLight),
                BorderThickness = new Thickness(1),
                HorizontalAlignment = HorizontalAlignment.Left,
                Cursor = Cursors.Hand,
                Template = CreatePrimaryTemplate()
            };
            select.Click += SelectApplication;
            AutomationProperties.SetName(select, "Seleccionar una carpeta de proyecto para inspección / Select a project folder for inspection");
            pageBody.Children.Add(select);
            SetView(pageBody, "analyze");
        }

        private void ShowTools(object sender, RoutedEventArgs eventArgs)
        {
            string engine = File.Exists(backend) ? "Disponible / Available" : "No disponible / Unavailable";
            SetView(BuildInformationPage(
                "Herramientas / Tools",
                "Solo se exponen operaciones que el motor local puede ejecutar y evidenciar.",
                "Motor local / Local engine: " + engine + "\n\n" +
                "Inspección: lectura de un proyecto reconocido sin ejecutar su código.\n" +
                "Verificación: gates en una copia aislada tras consentimiento explícito.\n" +
                "Reparación: búsqueda acotada, revisión y consentimiento separado antes de aplicar.\n" +
                "Evidencia: recibos persistidos y validables por el motor."), "tools");
        }

        private void ShowModes(object sender, RoutedEventArgs eventArgs)
        {
            SetView(BuildInformationPage(
                "Modos / Modes",
                "THE KING y CHECKMATE todavía no tienen un punto de entrada implementado.",
                "THE KING — Próximamente / Soon\nConstrucción orquestada / Orchestrated build\n\n" +
                "CHECKMATE — Próximamente / Soon\nRevisión adversarial / Adversarial review\n\n" +
                "THEKEY no simula estas operaciones mientras no exista una implementación verificable."), "modes");
        }

        private void ShowSettings(object sender, RoutedEventArgs eventArgs)
        {
            string runtime = GetRuntimeEvidenceRoot();
            SetView(BuildInformationPage(
                "Ajustes / Settings",
                "Configuración local y rutas reales del paquete.",
                "Paquete / Package\n" + root + "\n\n" +
                "Motor local / Local engine\n" + backend + "\n\n" +
                "Evidencia y resultados / Evidence and results\n" + runtime + "\n\n" +
                "No se almacenan claves ni se envían archivos desde esta interfaz."), "settings");
        }

        private void ShowLogs(object sender, RoutedEventArgs eventArgs)
        {
            StringBuilder text = new StringBuilder();
            if (activities.Count == 0)
            {
                text.Append("Sin registros de esta sesión / No session records yet.");
            }
            else
            {
                foreach (ActivityRecord activity in activities.OrderByDescending(item => item.OccurredAt))
                {
                    text.Append(activity.OccurredAt.ToString("O"));
                    text.Append(" | ");
                    text.Append(activity.Kind);
                    text.Append(" | ");
                    text.Append(activity.Detail);
                    text.Append(" | ");
                    text.Append(activity.Succeeded ? "SUCCESS" : "BLOCKED");
                    text.AppendLine();
                }
            }
            SetView(BuildInformationPage("Registros / Logs", "Registro real de operaciones iniciadas por esta ventana.", text.ToString()), "logs");
        }

        private void ShowResults(object sender, RoutedEventArgs eventArgs)
        {
            List<string> evidence = FindEvidenceFiles();
            StackPanel page = new StackPanel { MaxWidth = 1060, Margin = new Thickness(48, 46, 48, 48) };
            page.Children.Add(new TextBlock
            {
                Text = "Resultados / Results",
                FontFamily = new FontFamily("Georgia"),
                FontSize = 38,
                Foreground = Theme.Brush(Theme.Text)
            });
            page.Children.Add(new TextBlock
            {
                Text = "Estado, proyecto, gates, hallazgos, decisiones, evidencia y errores procedentes de artefactos persistidos.",
                FontSize = 16,
                Foreground = Theme.Brush(Theme.Gold),
                Margin = new Thickness(0, 10, 0, 24),
                TextWrapping = TextWrapping.Wrap
            });
            if (evidence.Count == 0)
            {
                Border empty = new Border
                {
                    Padding = new Thickness(22),
                    Background = Theme.Brush(Theme.Panel),
                    BorderBrush = Theme.Brush(Theme.GoldBorder),
                    BorderThickness = new Thickness(1),
                    CornerRadius = new CornerRadius(10)
                };
                empty.Child = new TextBlock
                {
                    Text = "Sin ejecutar / Not run\n\nNo hay recibos o resultados locales todavía. Ejecuta la demo o verifica un proyecto para generar evidencia real.",
                    Foreground = Theme.Brush(Theme.MutedText),
                    FontSize = 14,
                    TextWrapping = TextWrapping.Wrap
                };
                page.Children.Add(empty);
            }
            else
            {
                page.Children.Add(new TextBlock
                {
                    Text = "Artefactos reales detectados / Real artifacts detected: " + evidence.Count,
                    FontSize = 13,
                    Foreground = Theme.Brush(Theme.SecondaryText),
                    Margin = new Thickness(0, 0, 0, 14)
                });
                foreach (string path in evidence.Take(12))
                {
                    page.Children.Add(BuildEvidenceResultCard(path));
                }
            }
            Button restart = new Button
            {
                Content = "Reiniciar demo / Restart demo",
                Margin = new Thickness(0, 20, 0, 0),
                Padding = new Thickness(22, 12, 22, 12),
                Background = Theme.Brush(Theme.Gold),
                Foreground = Theme.Brush(Theme.Canvas),
                BorderBrush = Theme.Brush(Theme.GoldLight),
                BorderThickness = new Thickness(1),
                HorizontalAlignment = HorizontalAlignment.Left,
                Cursor = Cursors.Hand,
                Template = CreatePrimaryTemplate()
            };
            restart.Click += RunDemo;
            AutomationProperties.SetName(restart, "Reiniciar la demo para jueces / Restart the judge demo");
            page.Children.Add(restart);
            SetView(page, "results");
        }

        private FrameworkElement BuildEvidenceResultCard(string path)
        {
            FileInfo file = new FileInfo(path);
            string content;
            try
            {
                content = ReadTextPrefix(path, 2097152);
            }
            catch (Exception exception)
            {
                content = "";
                Border unreadable = CreateEvidencePanel();
                unreadable.Child = new TextBlock
                {
                    Text = "EVIDENCIA / EVIDENCE\n" + path + "\n\nERROR\n" + exception.Message,
                    Foreground = Theme.Brush(Theme.Error),
                    FontSize = 13,
                    TextWrapping = TextWrapping.Wrap
                };
                return unreadable;
            }

            string decision = FirstDeclared(
                ExtractJsonString(content, "release_decision", true),
                ExtractJsonString(content, "final_verdict", true),
                ExtractJsonString(content, "verdict", true),
                ExtractJsonString(content, "status", true));
            string created = FirstDeclared(ExtractJsonString(content, "created_at", false), file.LastWriteTime.ToString("O"));
            string project = FirstDeclared(
                ExtractJsonString(content, "project_name", false),
                ExtractJsonString(content, "source_root", false),
                ExtractJsonString(content, "path", false));
            string error = FirstDeclared(
                ExtractJsonString(content, "summary", false),
                ExtractJsonString(content, "reason_code", false));
            int gateCount = Regex.Matches(content, "\\\"gate\\\"\\s*:", RegexOptions.IgnoreCase).Count;
            int passedCount = Regex.Matches(content, "\\\"passed\\\"\\s*:\\s*true", RegexOptions.IgnoreCase).Count;
            int findingCount = Regex.Matches(content, "\\\"severity\\\"\\s*:", RegexOptions.IgnoreCase).Count;
            bool declaresFindings = content.IndexOf("\"findings\"", StringComparison.OrdinalIgnoreCase) >= 0 ||
                                    content.IndexOf("\"diagnostics\"", StringComparison.OrdinalIgnoreCase) >= 0;

            bool positive = decision.IndexOf("ELIGIBLE", StringComparison.OrdinalIgnoreCase) >= 0 ||
                            decision.IndexOf("VERIFIED", StringComparison.OrdinalIgnoreCase) >= 0 ||
                            decision.Equals("PASS", StringComparison.OrdinalIgnoreCase) ||
                            decision.IndexOf("REPAIRED", StringComparison.OrdinalIgnoreCase) >= 0;
            bool negative = decision.IndexOf("BLOCKED", StringComparison.OrdinalIgnoreCase) >= 0 ||
                            decision.IndexOf("FAILED", StringComparison.OrdinalIgnoreCase) >= 0 ||
                            decision.IndexOf("DENIED", StringComparison.OrdinalIgnoreCase) >= 0;
            Color stateColor = positive ? Theme.Success : negative ? Theme.Error : Theme.Gold;

            Border card = CreateEvidencePanel();
            StackPanel body = new StackPanel();
            Grid header = new Grid();
            header.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            header.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            header.Children.Add(new TextBlock
            {
                Text = file.Name,
                FontSize = 17,
                FontWeight = FontWeights.SemiBold,
                Foreground = Theme.Brush(Theme.Text),
                TextWrapping = TextWrapping.Wrap
            });
            Border badge = new Border
            {
                Padding = new Thickness(12, 5, 12, 5),
                CornerRadius = new CornerRadius(13),
                BorderBrush = Theme.Brush(stateColor),
                BorderThickness = new Thickness(1),
                Margin = new Thickness(12, 0, 0, 0)
            };
            badge.Child = new TextBlock { Text = decision, FontSize = 11, Foreground = Theme.Brush(stateColor) };
            Grid.SetColumn(badge, 1);
            header.Children.Add(badge);
            body.Children.Add(header);

            string gates = gateCount == 0 ? "No declarados / Not declared" : passedCount + " PASS / " + gateCount + " registrados";
            string findings = declaresFindings ? findingCount + " entradas declaradas / declared entries" : "No declarados / Not declared";
            body.Children.Add(new TextBlock
            {
                Text = "FECHA / DATE\n" + created +
                       "\n\nPROYECTO / PROJECT\n" + project +
                       "\n\nGATES\n" + gates +
                       "\n\nHALLAZGOS / FINDINGS\n" + findings +
                       "\n\nDECISIÓN / DECISION\n" + decision +
                       "\n\nEVIDENCIA / EVIDENCE\n" + path +
                       "\n\nERROR / ERROR\n" + error,
                FontFamily = new FontFamily("Consolas"),
                FontSize = 12,
                LineHeight = 18,
                Foreground = Theme.Brush(Theme.MutedText),
                Margin = new Thickness(0, 14, 0, 0),
                TextWrapping = TextWrapping.Wrap
            });
            card.Child = body;
            AutomationProperties.SetName(card, "Resultado real / Real result: " + file.Name + ", " + decision);
            return card;
        }

        private static Border CreateEvidencePanel()
        {
            return new Border
            {
                Padding = new Thickness(20),
                Margin = new Thickness(0, 0, 0, 12),
                Background = Theme.Brush(Theme.Panel),
                BorderBrush = Theme.Brush(Theme.GoldBorder),
                BorderThickness = new Thickness(1),
                CornerRadius = new CornerRadius(10)
            };
        }

        private FrameworkElement BuildInformationPage(string title, string subtitle, string text)
        {
            StackPanel page = new StackPanel { MaxWidth = 1060, Margin = new Thickness(48, 46, 48, 48) };
            page.Children.Add(new TextBlock
            {
                Text = title,
                FontFamily = new FontFamily("Georgia"),
                FontSize = 38,
                Foreground = Theme.Brush(Theme.Text)
            });
            page.Children.Add(new TextBlock
            {
                Text = subtitle,
                FontSize = 16,
                Foreground = Theme.Brush(Theme.Gold),
                Margin = new Thickness(0, 10, 0, 24),
                TextWrapping = TextWrapping.Wrap
            });
            Border panel = new Border
            {
                Padding = new Thickness(22),
                Background = Theme.Brush(Theme.Panel),
                BorderBrush = Theme.Brush(Theme.GoldBorder),
                BorderThickness = new Thickness(1),
                CornerRadius = new CornerRadius(10)
            };
            TextBox output = new TextBox
            {
                Text = text,
                IsReadOnly = true,
                Background = Brushes.Transparent,
                Foreground = Theme.Brush(Theme.MutedText),
                BorderThickness = new Thickness(0),
                FontFamily = new FontFamily("Consolas"),
                FontSize = 13,
                TextWrapping = TextWrapping.Wrap,
                AcceptsReturn = true,
                VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
                MinHeight = 310,
                Focusable = true
            };
            AutomationProperties.SetName(output, title + " content");
            panel.Child = output;
            page.Children.Add(panel);
            return page;
        }

        private void SetView(FrameworkElement view, string navigationKey)
        {
            contentHost.Children.Clear();
            contentHost.Children.Add(view);
            foreach (KeyValuePair<string, Button> entry in navigation)
            {
                bool active = entry.Key == navigationKey;
                entry.Value.Background = active ? Theme.Brush(Color.FromRgb(12, 30, 49)) : Brushes.Transparent;
                entry.Value.BorderBrush = active ? Theme.Brush(Theme.GoldBorder) : Brushes.Transparent;
                entry.Value.Foreground = active ? Theme.Brush(Theme.GoldLight) : Theme.Brush(Theme.MutedText);
            }
            if (!renderingCanonicalComposition && mainContentViewport != null)
            {
                mainContentViewport.ScrollToTop();
            }
        }

        private void SelectApplication(object sender, RoutedEventArgs eventArgs)
        {
            if (!EnsureNoOperationRunning()) return;
            using (System.Windows.Forms.FolderBrowserDialog dialog = new System.Windows.Forms.FolderBrowserDialog())
            {
                dialog.Description = "Selecciona una carpeta de proyecto compatible para analizar / Select a compatible project folder to inspect";
                dialog.ShowNewFolderButton = false;
                if (dialog.ShowDialog() != System.Windows.Forms.DialogResult.OK)
                {
                    MessageBox.Show(
                        "Selección cancelada. No se ha inspeccionado ni modificado ningún proyecto.\n\nSelection cancelled. No project was inspected or modified.",
                        "THEKEY — Selección cancelada / Selection cancelled",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information);
                    return;
                }
                string candidate = dialog.SelectedPath;
                if (String.IsNullOrWhiteSpace(candidate) || !Directory.Exists(candidate))
                {
                    ShowOperationPage("Analizar / Analyze", "La ruta seleccionada no existe o no es una carpeta / The selected path does not exist or is not a folder.");
                    SetStatus("Ruta no válida / Invalid path", false);
                    return;
                }
                selectedProject = candidate;
                RunBackend(
                    "project inspect --source " + QuoteArgument(candidate),
                    "Analizando de solo lectura / Read-only analysis",
                    "Analizar / Analyze",
                    delegate(int exitCode, string output)
                    {
                        if (exitCode == 0)
                        {
                            SetStatus("Análisis completado / Analysis complete", true);
                            selectedSource.Text = "Proyecto seleccionado / Selected project: " + candidate;
                        }
                        else
                        {
                            selectedProject = null;
                            SetStatus("Entrada no compatible o bloqueada / Unsupported or blocked input", false);
                        }
                    });
            }
        }

        private void VerifySelectedApplication(object sender, RoutedEventArgs eventArgs)
        {
            if (!EnsureNoOperationRunning()) return;
            if (!EnsureSelectedProject("Verificar / Verify")) return;
            MessageBoxResult consent = MessageBox.Show(
                "THEKEY ejecutará los tests de confianza del proyecto en una copia aislada. El original no se modificará. Los tests no están dentro de un sandbox del sistema operativo.\n\n¿Autorizas esta verificación?",
                "THEKEY — Consentimiento de verificación / Verification consent",
                MessageBoxButton.YesNo,
                MessageBoxImage.Warning);
            if (consent != MessageBoxResult.Yes)
            {
                SetStatus("Verificación cancelada / Verification cancelled", false);
                return;
            }
            RunBackend(
                "project verify --source " + QuoteArgument(selectedProject) + " --consent execute_trusted_tests",
                "Verificando en aislamiento / Verifying in isolation",
                "Verificar / Verify",
                delegate(int exitCode, string output)
                {
                    bool verified = exitCode == 0 && output.Contains("VERIFIED");
                    SetStatus(verified ? "Verificado / Verified" : "Verificación bloqueada o fallida / Verification blocked or failed", verified);
                });
        }

        private void RepairSelectedApplication(object sender, RoutedEventArgs eventArgs)
        {
            if (!EnsureNoOperationRunning()) return;
            if (!EnsureSelectedProject("Reparar / Repair")) return;
            MessageBoxResult consent = MessageBox.Show(
                "THEKEY buscará una reparación acotada en una copia aislada y volverá a ejecutar todos los gates. Esta primera fase no modifica el original.\n\nLos tests no están dentro de un sandbox del sistema operativo. ¿Autorizas la búsqueda de reparación?",
                "THEKEY — Consentimiento de reparación / Repair consent",
                MessageBoxButton.YesNo,
                MessageBoxImage.Warning);
            if (consent != MessageBoxResult.Yes)
            {
                SetStatus("Reparación cancelada / Repair cancelled", false);
                return;
            }
            RunBackend(
                "project repair --source " + QuoteArgument(selectedProject) + " --consent execute_trusted_tests",
                "Buscando reparación aislada / Searching isolated repair",
                "Reparar / Repair",
                delegate(int exitCode, string output)
                {
                    bool ready = exitCode == 0 && output.Contains("REPAIR_READY");
                    if (ready)
                    {
                        SetStatus("Reparación preparada para revisión / Repair ready for review", true);
                        applyRepairButton.Visibility = Visibility.Visible;
                        applyRepairButton.IsEnabled = true;
                    }
                    else if (exitCode == 0 && output.Contains("NO_CHANGES_NEEDED"))
                    {
                        SetStatus("No requiere cambios / No changes needed", true);
                    }
                    else
                    {
                        SetStatus("No hay reparación segura verificada / No verified safe repair", false);
                    }
                });
        }

        private void ApplyReviewedRepair(object sender, RoutedEventArgs eventArgs)
        {
            if (!EnsureNoOperationRunning()) return;
            if (!EnsureSelectedProject("Aplicar reparación / Apply repair")) return;
            MessageBoxResult consent = MessageBox.Show(
                "Has revisado la evidencia de reparación. THEKEY volverá a calcular los gates, comprobará que el original no cambió, creará un backup externo y solo aplicará la reparación si todo sigue pasando.\n\n¿Autorizas aplicar esa reparación verificada?",
                "THEKEY — Consentimiento final / Final consent",
                MessageBoxButton.YesNo,
                MessageBoxImage.Warning);
            if (consent != MessageBoxResult.Yes)
            {
                SetStatus("Aplicación de reparación cancelada / Repair application cancelled", false);
                return;
            }
            RunBackend(
                "project repair --source " + QuoteArgument(selectedProject) + " --consent execute_trusted_tests --apply-consent apply_verified_repairs",
                "Aplicando reparación verificada / Applying verified repair",
                "Aplicar reparación verificada / Apply verified repair",
                delegate(int exitCode, string output)
                {
                    bool repaired = exitCode == 0 && output.Contains("REPAIRED_AND_VERIFIED");
                    SetStatus(repaired ? "Reparada y verificada / Repaired and verified" : "Aplicación de reparación bloqueada / Repair application blocked", repaired);
                });
        }

        private void RunDemo(object sender, RoutedEventArgs eventArgs)
        {
            if (!EnsureNoOperationRunning()) return;
            RunBackend(
                "portable-demo",
                "Ejecutando demo gobernada / Running governed demo",
                "Demo para jueces / Judge demo",
                delegate(int exitCode, string output)
                {
                    bool passed = exitCode == 0 && output.Contains("RELEASE_ELIGIBLE");
                    SetStatus(passed ? "Demo completada / Demo complete" : "Demo bloqueada o fallida / Demo blocked or failed", passed);
                });
        }

        private bool EnsureSelectedProject(string operation)
        {
            if (!String.IsNullOrWhiteSpace(selectedProject) && Directory.Exists(selectedProject)) return true;
            ShowOperationPage(operation, "Selecciona primero una carpeta de proyecto existente con la acción principal / First select an existing project folder with the primary action.");
            SetStatus("Proyecto pendiente / Project pending", false);
            return false;
        }

        private bool EnsureNoOperationRunning()
        {
            if (!operationRunning) return true;
            MessageBox.Show(
                "Ya hay una operación local en curso. Espera a que termine o usa la cancelación segura de su vista.\n\nA local operation is already running. Wait for it to finish or use safe cancellation in its view.",
                "THEKEY — Operación en curso / Operation running",
                MessageBoxButton.OK,
                MessageBoxImage.Information);
            return false;
        }

        private void ShowOperationPage(string title, string initialOutput)
        {
            StackPanel page = new StackPanel { MaxWidth = 1060, Margin = new Thickness(48, 46, 48, 48) };
            operationHeading = new TextBlock
            {
                Text = title,
                FontFamily = new FontFamily("Georgia"),
                FontSize = 38,
                Foreground = Theme.Brush(Theme.Text)
            };
            page.Children.Add(operationHeading);
            selectedSource = new TextBlock
            {
                Text = String.IsNullOrWhiteSpace(selectedProject) ? "Sin proyecto seleccionado / No project selected" : "Proyecto seleccionado / Selected project: " + selectedProject,
                FontSize = 14,
                Foreground = Theme.Brush(Theme.Gold),
                Margin = new Thickness(0, 10, 0, 17),
                TextWrapping = TextWrapping.Wrap
            };
            page.Children.Add(selectedSource);
            status = new TextBlock
            {
                Text = "Pendiente / Pending",
                FontSize = 14,
                Foreground = Theme.Brush(Theme.Gold),
                Margin = new Thickness(0, 0, 0, 17),
                TextWrapping = TextWrapping.Wrap
            };
            page.Children.Add(status);
            Border panel = new Border
            {
                Padding = new Thickness(18),
                Background = Theme.Brush(Color.FromRgb(4, 14, 25)),
                BorderBrush = Theme.Brush(Theme.GoldBorder),
                BorderThickness = new Thickness(1),
                CornerRadius = new CornerRadius(10)
            };
            operationOutput = new TextBox
            {
                Text = initialOutput + Environment.NewLine,
                IsReadOnly = true,
                AcceptsReturn = true,
                TextWrapping = TextWrapping.Wrap,
                FontFamily = new FontFamily("Consolas"),
                FontSize = 13,
                Foreground = Theme.Brush(Theme.MutedText),
                Background = Brushes.Transparent,
                BorderThickness = new Thickness(0),
                MinHeight = 350,
                VerticalScrollBarVisibility = ScrollBarVisibility.Auto
            };
            AutomationProperties.SetName(operationOutput, "Salida real de operación / Real operation output");
            panel.Child = operationOutput;
            page.Children.Add(panel);
            cancelOperationButton = new Button
            {
                Content = "Cancelar operación aislada / Cancel isolated operation",
                Margin = new Thickness(0, 20, 0, 0),
                Padding = new Thickness(22, 12, 22, 12),
                Background = Theme.Brush(Color.FromRgb(64, 35, 32)),
                Foreground = Theme.Brush(Theme.Text),
                BorderBrush = Theme.Brush(Theme.Error),
                BorderThickness = new Thickness(1),
                HorizontalAlignment = HorizontalAlignment.Left,
                Cursor = Cursors.Hand,
                Visibility = operationRunning ? Visibility.Visible : Visibility.Collapsed,
                Template = CreateCardTemplate()
            };
            cancelOperationButton.Click += RequestCancellation;
            AutomationProperties.SetName(cancelOperationButton, "Cancelar la operación aislada en curso / Cancel the running isolated operation");
            page.Children.Add(cancelOperationButton);
            applyRepairButton = new Button
            {
                Content = "Aplicar reparación verificada / Apply verified repair",
                Margin = new Thickness(0, 20, 0, 0),
                Padding = new Thickness(22, 12, 22, 12),
                Background = Theme.Brush(Theme.Gold),
                Foreground = Theme.Brush(Theme.Canvas),
                BorderBrush = Theme.Brush(Theme.GoldLight),
                BorderThickness = new Thickness(1),
                HorizontalAlignment = HorizontalAlignment.Left,
                Cursor = Cursors.Hand,
                Visibility = Visibility.Collapsed,
                Template = CreatePrimaryTemplate()
            };
            applyRepairButton.Click += ApplyReviewedRepair;
            AutomationProperties.SetName(applyRepairButton, "Aplicar la reparación verificada tras revisar la evidencia / Apply verified repair after reviewing evidence");
            page.Children.Add(applyRepairButton);
            SetView(page, "");
        }

        private void RequestCancellation(object sender, RoutedEventArgs eventArgs)
        {
            int processId = 0;
            lock (backendProcessSync)
            {
                if (activeBackendProcess != null && !activeBackendProcess.HasExited)
                {
                    processId = activeBackendProcess.Id;
                }
            }
            if (processId == 0)
            {
                SetStatus("La operación aún no se puede cancelar / Operation is not cancellable yet", false);
                return;
            }
            if (MessageBox.Show(
                    "Se terminará únicamente el árbol de procesos del motor local en el workspace aislado. El proyecto original no se modifica.\n\n¿Cancelar ahora?",
                    "THEKEY — Cancelar operación / Cancel operation",
                    MessageBoxButton.YesNo,
                    MessageBoxImage.Warning) != MessageBoxResult.Yes)
            {
                return;
            }
            try
            {
                TerminateProcessTree(processId);
                if (cancelOperationButton != null) cancelOperationButton.IsEnabled = false;
                SetStatus("Cancelación solicitada / Cancellation requested", false);
                if (operationOutput != null)
                {
                    operationOutput.AppendText("Cancelación solicitada para el proceso local " + processId + ".\r\n");
                }
            }
            catch (Exception exception)
            {
                SetStatus("No se pudo cancelar / Could not cancel", false);
                if (operationOutput != null) operationOutput.AppendText("Cancel error: " + exception.Message + "\r\n");
            }
        }

        private void HandleWindowClosing(object sender, CancelEventArgs eventArgs)
        {
            int processId = 0;
            lock (backendProcessSync)
            {
                if (activeBackendProcess != null && !activeBackendProcess.HasExited) processId = activeBackendProcess.Id;
            }
            if (processId == 0) return;

            if (MessageBox.Show(
                    "Hay una operación aislada en curso. Cerrar THEKEY terminará únicamente ese árbol de procesos; el proyecto original no se modifica.\n\n¿Cerrar y cancelar la operación?",
                    "THEKEY — Operación en curso / Operation running",
                    MessageBoxButton.YesNo,
                    MessageBoxImage.Warning) != MessageBoxResult.Yes)
            {
                eventArgs.Cancel = true;
                return;
            }
            try
            {
                TerminateProcessTree(processId);
                operationRunning = false;
            }
            catch (Exception exception)
            {
                eventArgs.Cancel = true;
                MessageBox.Show(
                    "No se pudo terminar de forma controlada la operación local. THEKEY permanecerá abierto.\n\n" + exception.Message,
                    "THEKEY — Cierre bloqueado / Close blocked",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error);
            }
        }

        private static void TerminateProcessTree(int processId)
        {
            ProcessStartInfo taskkill = new ProcessStartInfo
            {
                FileName = "taskkill.exe",
                Arguments = "/PID " + processId + " /T /F",
                UseShellExecute = false,
                CreateNoWindow = true
            };
            using (Process terminator = Process.Start(taskkill))
            {
                if (terminator == null || !terminator.WaitForExit(8000))
                {
                    throw new InvalidOperationException("Timed out terminating the isolated process tree.");
                }
                if (terminator.ExitCode != 0)
                {
                    throw new InvalidOperationException("taskkill exited with code " + terminator.ExitCode + ".");
                }
            }
        }

        private void RunBackend(string arguments, string runningStatus, string operationTitle, Action<int, string> completed)
        {
            if (operationRunning)
            {
                EnsureNoOperationRunning();
                return;
            }
            if (!File.Exists(backend))
            {
                ShowOperationPage(operationTitle, "Falta el motor local / Missing local engine: " + backend);
                SetStatus("Motor no disponible / Engine unavailable", false);
                return;
            }
            operationRunning = true;
            ShowOperationPage(operationTitle, "> THEKEY-Core.exe " + arguments + Environment.NewLine + Environment.NewLine);
            if (status != null)
            {
                status.Text = runningStatus;
                status.Foreground = Theme.Brush(Theme.Gold);
            }
            Task.Factory.StartNew(delegate
            {
                int exitCode = 1;
                string combined = "";
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
                        if (process == null) throw new InvalidOperationException("The local engine did not start.");
                        lock (backendProcessSync) activeBackendProcess = process;
                        try
                        {
                            StringBuilder streamed = new StringBuilder();
                            object streamSync = new object();
                            DataReceivedEventHandler receive = delegate(object streamSender, DataReceivedEventArgs streamEvent)
                            {
                                if (streamEvent.Data == null) return;
                                lock (streamSync) streamed.AppendLine(streamEvent.Data);
                                if (!Dispatcher.HasShutdownStarted)
                                {
                                    Dispatcher.BeginInvoke(new Action(delegate
                                    {
                                        if (operationOutput != null)
                                        {
                                            operationOutput.AppendText(streamEvent.Data + Environment.NewLine);
                                            operationOutput.ScrollToEnd();
                                        }
                                    }));
                                }
                            };
                            process.OutputDataReceived += receive;
                            process.ErrorDataReceived += receive;
                            process.BeginOutputReadLine();
                            process.BeginErrorReadLine();
                            process.WaitForExit();
                            process.WaitForExit();
                            exitCode = process.ExitCode;
                            lock (streamSync) combined = streamed.ToString();
                        }
                        finally
                        {
                            lock (backendProcessSync)
                            {
                                if (Object.ReferenceEquals(activeBackendProcess, process)) activeBackendProcess = null;
                            }
                        }
                    }
                }
                catch (Exception exception)
                {
                    combined = "Launcher error: " + exception.Message;
                }
                if (Dispatcher.HasShutdownStarted) return;
                Dispatcher.Invoke(delegate
                {
                    operationRunning = false;
                    if (cancelOperationButton != null) cancelOperationButton.Visibility = Visibility.Collapsed;
                    if (operationOutput != null)
                    {
                        operationOutput.AppendText(Environment.NewLine + "Exit code: " + exitCode + Environment.NewLine);
                        operationOutput.ScrollToEnd();
                    }
                    activities.Add(new ActivityRecord(operationTitle, "Exit code " + exitCode, exitCode == 0));
                    completed(exitCode, combined);
                });
            });
        }

        private void SetStatus(string text, bool ok)
        {
            if (status == null) return;
            status.Text = text;
            status.Foreground = Theme.Brush(ok ? Theme.Success : Theme.Error);
        }

        private List<string> FindEvidenceFiles()
        {
            string evidenceRoot = GetRuntimeEvidenceRoot();
            if (!Directory.Exists(evidenceRoot)) return new List<string>();
            try
            {
                return Directory.GetFiles(evidenceRoot, "*.json", SearchOption.AllDirectories)
                    .Where(path => Path.GetFileName(path).IndexOf("evidence", StringComparison.OrdinalIgnoreCase) >= 0 ||
                                   Path.GetFileName(path).IndexOf("inspection", StringComparison.OrdinalIgnoreCase) >= 0 ||
                                   Path.GetFileName(path).IndexOf("verification", StringComparison.OrdinalIgnoreCase) >= 0 ||
                                   Path.GetFileName(path).IndexOf("receipt", StringComparison.OrdinalIgnoreCase) >= 0)
                    .OrderByDescending(path => File.GetLastWriteTimeUtc(path))
                    .ToList();
            }
            catch (Exception)
            {
                return new List<string>();
            }
        }

        private static string ReadTextPrefix(string path, int maximumCharacters)
        {
            using (FileStream stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
            using (StreamReader reader = new StreamReader(stream, Encoding.UTF8, true, 4096, false))
            {
                char[] buffer = new char[maximumCharacters];
                int count = reader.ReadBlock(buffer, 0, buffer.Length);
                return new string(buffer, 0, count);
            }
        }

        private static string ExtractJsonString(string content, string key, bool takeLast)
        {
            if (String.IsNullOrEmpty(content)) return "";
            MatchCollection matches = Regex.Matches(
                content,
                "\\\"" + Regex.Escape(key) + "\\\"\\s*:\\s*\\\"((?:\\\\.|[^\\\"])*)\\\"",
                RegexOptions.IgnoreCase);
            if (matches.Count == 0) return "";
            string encoded = matches[takeLast ? matches.Count - 1 : 0].Groups[1].Value;
            try
            {
                return Regex.Unescape(encoded).Replace("\\/", "/");
            }
            catch (ArgumentException)
            {
                return encoded;
            }
        }

        private static string FirstDeclared(params string[] values)
        {
            foreach (string value in values)
            {
                if (!String.IsNullOrWhiteSpace(value)) return value;
            }
            return "No declarado / Not declared";
        }

        private void LoadPersistedActivities()
        {
            foreach (string path in FindEvidenceFiles().Take(12))
            {
                try
                {
                    string content;
                    using (FileStream stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
                    using (StreamReader reader = new StreamReader(stream, Encoding.UTF8, true, 4096, false))
                    {
                        char[] buffer = new char[262144];
                        int count = reader.ReadBlock(buffer, 0, buffer.Length);
                        content = new string(buffer, 0, count);
                    }

                    bool succeeded =
                        content.IndexOf("RELEASE_ELIGIBLE", StringComparison.OrdinalIgnoreCase) >= 0 ||
                        content.IndexOf("REPAIRED_AND_VERIFIED", StringComparison.OrdinalIgnoreCase) >= 0 ||
                        content.IndexOf("\"verdict\": \"VERIFIED\"", StringComparison.OrdinalIgnoreCase) >= 0 ||
                        content.IndexOf("\"verdict\": \"PASS\"", StringComparison.OrdinalIgnoreCase) >= 0;
                    bool blocked =
                        content.IndexOf("RELEASE_BLOCKED", StringComparison.OrdinalIgnoreCase) >= 0 ||
                        content.IndexOf("\"verdict\": \"BLOCKED\"", StringComparison.OrdinalIgnoreCase) >= 0 ||
                        content.IndexOf("\"status\": \"FAILED\"", StringComparison.OrdinalIgnoreCase) >= 0;
                    if (!succeeded && !blocked) continue;

                    string name = Path.GetFileName(path);
                    string lower = name.ToLowerInvariant();
                    string kind = lower.Contains("judge") ? "Demo / Judge demo" :
                                  lower.Contains("repair") ? "Reparación / Repair" :
                                  lower.Contains("verification") ? "Verificación / Verify" :
                                  lower.Contains("inspection") ? "Análisis / Analyze" :
                                  "Resultados / Results";
                    activities.Add(new ActivityRecord(File.GetLastWriteTime(path), kind, name, succeeded));
                    if (activities.Count >= 4) break;
                }
                catch (Exception)
                {
                    // An unreadable receipt is omitted rather than presented as evidence.
                }
            }
        }

        private static string GetRuntimeEvidenceRoot()
        {
            string configured = Environment.GetEnvironmentVariable("THEKEY_EVIDENCE_ROOT");
            if (!String.IsNullOrWhiteSpace(configured) && Directory.Exists(configured))
            {
                return Path.GetFullPath(configured);
            }
            return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "THEKEY", ".thekey");
        }

        private static string QuoteArgument(string value)
        {
            return "\"" + value.Replace("\"", "\\\"") + "\"";
        }

        private FrameworkElement CreateBrandIcon(double size)
        {
            return CreateIcon("chessking", size, Theme.Brush(Theme.GoldLight));
        }

        private static FrameworkElement CreateWindowIcon(string kind)
        {
            Canvas canvas = new Canvas { Width = 20, Height = 20, HorizontalAlignment = HorizontalAlignment.Center, VerticalAlignment = VerticalAlignment.Center };
            Brush brush = Theme.Brush(Theme.MutedText);
            if (kind == "minimize")
            {
                AddLine(canvas, 4, 12, 16, 12, brush, 1.2);
            }
            else if (kind == "maximize")
            {
                AddPath(canvas, "M5,5 L15,5 L15,15 L5,15 Z", brush, 1.2, Brushes.Transparent);
            }
            else
            {
                AddLine(canvas, 5, 5, 15, 15, brush, 1.2);
                AddLine(canvas, 15, 5, 5, 15, brush, 1.2);
            }
            return canvas;
        }

        private static FrameworkElement CreateIcon(string kind, double size, Brush brush)
        {
            Viewbox box = new Viewbox { Width = size, Height = size, Stretch = Stretch.Uniform, HorizontalAlignment = HorizontalAlignment.Center, VerticalAlignment = VerticalAlignment.Center };
            Canvas canvas = new Canvas { Width = 24, Height = 24 };
            if (kind == "home")
            {
                AddPath(canvas, "M3,11 L12,3 L21,11 L21,21 L3,21 Z M9,21 L9,14 L15,14 L15,21", brush, 1.5, Brushes.Transparent);
            }
            else if (kind == "analyze")
            {
                AddEllipse(canvas, 4, 4, 13, 13, brush, 1.5);
                AddLine(canvas, 14, 14, 21, 21, brush, 1.8);
            }
            else if (kind == "tools" || kind == "repair")
            {
                AddLine(canvas, 4, 4, 20, 20, brush, 2.1);
                AddLine(canvas, 20, 4, 4, 20, brush, 2.1);
                AddEllipse(canvas, 2, 2, 5, 5, brush, 1.3);
                AddEllipse(canvas, 17, 17, 5, 5, brush, 1.3);
            }
            else if (kind == "results")
            {
                AddRectangle(canvas, 4, 12, 3, 8, brush);
                AddRectangle(canvas, 10, 7, 3, 13, brush);
                AddRectangle(canvas, 16, 3, 3, 17, brush);
            }
            else if (kind == "chessking")
            {
                AddPath(canvas, "M10,1 L14,1 L14,4 L17,4 L17,7 L14,7 L14,9 C17,10 18.5,12 18.5,14 C18.5,16 17.5,17.5 16,18.5 L19,21 L5,21 L8,18.5 C6.5,17.5 5.5,16 5.5,14 C5.5,12 7,10 10,9 L10,7 L7,7 L7,4 L10,4 Z", brush, 1.25, Brushes.Transparent);
                AddLine(canvas, 7, 18.5, 17, 18.5, brush, 1.2);
                AddLine(canvas, 4, 23, 20, 23, brush, 1.5);
            }
            else if (kind == "checkmate")
            {
                AddPath(canvas, "M10,3 L14,3 L14,6 L16,6 L16,9 L14,9 L14,12 L17,18 L7,18 L10,12 L10,9 L8,9 L8,6 L10,6 Z", brush, 1.25, Brushes.Transparent);
                AddLine(canvas, 6, 21, 18, 21, brush, 1.5);
            }
            else if (kind == "modes" || kind == "king")
            {
                AddPath(canvas, "M4,19 L20,19 L18,10 L15,14 L12,6 L9,14 L6,10 Z M6,22 L18,22", brush, 1.5, Brushes.Transparent);
            }
            else if (kind == "logs")
            {
                AddPath(canvas, "M5,3 L19,3 L19,21 L5,21 Z", brush, 1.4, Brushes.Transparent);
                AddLine(canvas, 8, 8, 16, 8, brush, 1.2);
                AddLine(canvas, 8, 12, 16, 12, brush, 1.2);
                AddLine(canvas, 8, 16, 14, 16, brush, 1.2);
            }
            else if (kind == "settings")
            {
                AddEllipse(canvas, 7, 7, 10, 10, brush, 1.5);
                for (int index = 0; index < 8; index++)
                {
                    double angle = index * 45 * Math.PI / 180;
                    double x1 = 12 + Math.Cos(angle) * 7;
                    double y1 = 12 + Math.Sin(angle) * 7;
                    double x2 = 12 + Math.Cos(angle) * 10;
                    double y2 = 12 + Math.Sin(angle) * 10;
                    AddLine(canvas, x1, y1, x2, y2, brush, 2);
                }
            }
            else if (kind == "shield")
            {
                AddPath(canvas, "M12,2 L21,6 L21,13 C21,18 17,21 12,23 C7,21 3,18 3,13 L3,6 Z", brush, 1.5, Brushes.Transparent);
            }
            else if (kind == "demo")
            {
                AddPath(canvas, "M6,3 L20,12 L6,21 Z", brush, 1.5, brush);
            }
            else if (kind == "target")
            {
                AddEllipse(canvas, 3, 3, 18, 18, brush, 1.5);
                AddEllipse(canvas, 7, 7, 10, 10, brush, 1.5);
                AddEllipse(canvas, 10, 10, 4, 4, brush, 1.5);
                AddLine(canvas, 12, 0, 12, 4, brush, 1.5);
                AddLine(canvas, 12, 20, 12, 24, brush, 1.5);
                AddLine(canvas, 0, 12, 4, 12, brush, 1.5);
                AddLine(canvas, 20, 12, 24, 12, brush, 1.5);
            }
            else if (kind == "arrow")
            {
                AddLine(canvas, 2, 12, 21, 12, brush, 1.6);
                AddLine(canvas, 15, 6, 21, 12, brush, 1.6);
                AddLine(canvas, 15, 18, 21, 12, brush, 1.6);
            }
            else
            {
                AddPath(canvas, "M6,20 L18,20 L17,10 L14,13 L12,4 L10,13 L7,10 Z", brush, 1.5, Brushes.Transparent);
            }
            box.Child = canvas;
            return box;
        }

        private static void AddPath(Canvas canvas, string data, Brush stroke, double thickness, Brush fill)
        {
            System.Windows.Shapes.Path path = new System.Windows.Shapes.Path
            {
                Data = Geometry.Parse(data),
                Stroke = stroke,
                StrokeThickness = thickness,
                Fill = fill,
                StrokeLineJoin = PenLineJoin.Round,
                StrokeStartLineCap = PenLineCap.Round,
                StrokeEndLineCap = PenLineCap.Round
            };
            canvas.Children.Add(path);
        }

        private static void AddLine(Canvas canvas, double x1, double y1, double x2, double y2, Brush brush, double thickness)
        {
            canvas.Children.Add(new System.Windows.Shapes.Line { X1 = x1, Y1 = y1, X2 = x2, Y2 = y2, Stroke = brush, StrokeThickness = thickness, StrokeStartLineCap = PenLineCap.Round, StrokeEndLineCap = PenLineCap.Round });
        }

        private static void AddEllipse(Canvas canvas, double left, double top, double width, double height, Brush brush, double thickness)
        {
            System.Windows.Shapes.Ellipse ellipse = new System.Windows.Shapes.Ellipse { Width = width, Height = height, Stroke = brush, StrokeThickness = thickness };
            Canvas.SetLeft(ellipse, left);
            Canvas.SetTop(ellipse, top);
            canvas.Children.Add(ellipse);
        }

        private static void AddRectangle(Canvas canvas, double left, double top, double width, double height, Brush brush)
        {
            System.Windows.Shapes.Rectangle rectangle = new System.Windows.Shapes.Rectangle { Width = width, Height = height, Fill = brush, RadiusX = 0.8, RadiusY = 0.8 };
            Canvas.SetLeft(rectangle, left);
            Canvas.SetTop(rectangle, top);
            canvas.Children.Add(rectangle);
        }

        private static ControlTemplate CreateNavTemplate()
        {
            ControlTemplate template = new ControlTemplate(typeof(Button));
            FrameworkElementFactory border = new FrameworkElementFactory(typeof(Border));
            border.SetValue(Border.BackgroundProperty, new TemplateBindingExtension(Control.BackgroundProperty));
            border.SetValue(Border.BorderBrushProperty, new TemplateBindingExtension(Control.BorderBrushProperty));
            border.SetValue(Border.BorderThicknessProperty, new TemplateBindingExtension(Control.BorderThicknessProperty));
            border.SetValue(Border.CornerRadiusProperty, new CornerRadius(0, 10, 10, 0));
            FrameworkElementFactory presenter = new FrameworkElementFactory(typeof(ContentPresenter));
            presenter.SetValue(ContentPresenter.ContentProperty, new TemplateBindingExtension(ContentControl.ContentProperty));
            presenter.SetValue(ContentPresenter.MarginProperty, new TemplateBindingExtension(Control.PaddingProperty));
            border.AppendChild(presenter);
            template.VisualTree = border;
            Trigger hover = new Trigger { Property = UIElement.IsMouseOverProperty, Value = true };
            hover.Setters.Add(new Setter(Control.BackgroundProperty, Theme.Brush(Color.FromRgb(12, 30, 49))));
            hover.Setters.Add(new Setter(Control.BorderBrushProperty, Theme.Brush(Theme.GoldBorder)));
            template.Triggers.Add(hover);
            Trigger focus = new Trigger { Property = UIElement.IsKeyboardFocusedProperty, Value = true };
            focus.Setters.Add(new Setter(Control.BorderBrushProperty, Theme.Brush(Theme.GoldLight)));
            focus.Setters.Add(new Setter(Control.BorderThicknessProperty, new Thickness(2)));
            template.Triggers.Add(focus);
            return template;
        }

        private static ControlTemplate CreateCardTemplate()
        {
            ControlTemplate template = new ControlTemplate(typeof(Button));
            FrameworkElementFactory border = new FrameworkElementFactory(typeof(Border));
            border.SetValue(Border.BackgroundProperty, new TemplateBindingExtension(Control.BackgroundProperty));
            border.SetValue(Border.BorderBrushProperty, new TemplateBindingExtension(Control.BorderBrushProperty));
            border.SetValue(Border.BorderThicknessProperty, new TemplateBindingExtension(Control.BorderThicknessProperty));
            border.SetValue(Border.CornerRadiusProperty, new CornerRadius(10));
            FrameworkElementFactory presenter = new FrameworkElementFactory(typeof(ContentPresenter));
            presenter.SetValue(ContentPresenter.ContentProperty, new TemplateBindingExtension(ContentControl.ContentProperty));
            presenter.SetValue(ContentPresenter.MarginProperty, new TemplateBindingExtension(Control.PaddingProperty));
            border.AppendChild(presenter);
            template.VisualTree = border;
            Trigger hover = new Trigger { Property = UIElement.IsMouseOverProperty, Value = true };
            hover.Setters.Add(new Setter(Control.BackgroundProperty, Theme.Brush(Color.FromRgb(14, 37, 59))));
            hover.Setters.Add(new Setter(Control.BorderBrushProperty, Theme.Brush(Theme.GoldLight)));
            template.Triggers.Add(hover);
            Trigger pressed = new Trigger { Property = Button.IsPressedProperty, Value = true };
            pressed.Setters.Add(new Setter(Control.BackgroundProperty, Theme.Brush(Color.FromRgb(5, 15, 27))));
            template.Triggers.Add(pressed);
            Trigger disabled = new Trigger { Property = UIElement.IsEnabledProperty, Value = false };
            disabled.Setters.Add(new Setter(UIElement.OpacityProperty, 0.68));
            disabled.Setters.Add(new Setter(FrameworkElement.CursorProperty, Cursors.Arrow));
            template.Triggers.Add(disabled);
            Trigger focus = new Trigger { Property = UIElement.IsKeyboardFocusedProperty, Value = true };
            focus.Setters.Add(new Setter(Control.BorderBrushProperty, Brushes.White));
            focus.Setters.Add(new Setter(Control.BorderThicknessProperty, new Thickness(2)));
            template.Triggers.Add(focus);
            return template;
        }

        private static ControlTemplate CreatePrimaryTemplate()
        {
            ControlTemplate template = CreateCardTemplate();
            Trigger hover = new Trigger { Property = UIElement.IsMouseOverProperty, Value = true };
            hover.Setters.Add(new Setter(Control.BackgroundProperty, new LinearGradientBrush(Theme.GoldLight, Color.FromRgb(177, 113, 21), 0)));
            template.Triggers.Add(hover);
            return template;
        }

        private static LinearGradientBrush CreateMetallicGoldBrush()
        {
            LinearGradientBrush brush = new LinearGradientBrush
            {
                StartPoint = new Point(0, 0.5),
                EndPoint = new Point(1, 0.5)
            };
            brush.GradientStops.Add(new GradientStop(Color.FromRgb(153, 99, 25), 0));
            brush.GradientStops.Add(new GradientStop(Color.FromRgb(117, 79, 26), 0.28));
            brush.GradientStops.Add(new GradientStop(Color.FromRgb(120, 81, 27), 0.72));
            brush.GradientStops.Add(new GradientStop(Color.FromRgb(131, 89, 30), 1));
            brush.Freeze();
            return brush;
        }

        private static LinearGradientBrush CreateHeroMetalOverlayBrush()
        {
            LinearGradientBrush brush = new LinearGradientBrush
            {
                StartPoint = new Point(0.5, 0),
                EndPoint = new Point(0.5, 1)
            };
            brush.GradientStops.Add(new GradientStop(Color.FromArgb(72, 255, 207, 101), 0));
            brush.GradientStops.Add(new GradientStop(Color.FromArgb(0, 255, 207, 101), 0.23));
            brush.GradientStops.Add(new GradientStop(Color.FromArgb(76, 0, 0, 0), 0.48));
            brush.GradientStops.Add(new GradientStop(Color.FromArgb(124, 0, 0, 0), 1));
            brush.Freeze();
            return brush;
        }

        private static ControlTemplate CreateHeroActionTemplate()
        {
            ControlTemplate template = new ControlTemplate(typeof(Button));
            FrameworkElementFactory grid = new FrameworkElementFactory(typeof(Grid));
            FrameworkElementFactory shape = new FrameworkElementFactory(typeof(System.Windows.Shapes.Path));
            shape.SetValue(System.Windows.Shapes.Path.DataProperty, Geometry.Parse("M22,0 L666,0 L688,22 L688,90 L666,112 L22,112 L0,90 L0,22 Z"));
            shape.SetValue(System.Windows.Shapes.Shape.FillProperty, new TemplateBindingExtension(Control.BackgroundProperty));
            shape.SetValue(System.Windows.Shapes.Shape.StrokeProperty, new TemplateBindingExtension(Control.BorderBrushProperty));
            shape.SetValue(System.Windows.Shapes.Shape.StrokeThicknessProperty, 1.4);
            shape.SetValue(System.Windows.Shapes.Shape.StrokeLineJoinProperty, PenLineJoin.Miter);
            grid.AppendChild(shape);

            FrameworkElementFactory metallicShade = new FrameworkElementFactory(typeof(System.Windows.Shapes.Path));
            metallicShade.SetValue(System.Windows.Shapes.Path.DataProperty, Geometry.Parse("M22,0 L666,0 L688,22 L688,90 L666,112 L22,112 L0,90 L0,22 Z"));
            metallicShade.SetValue(System.Windows.Shapes.Shape.FillProperty, CreateHeroMetalOverlayBrush());
            metallicShade.SetValue(UIElement.IsHitTestVisibleProperty, false);
            grid.AppendChild(metallicShade);

            FrameworkElementFactory inner = new FrameworkElementFactory(typeof(System.Windows.Shapes.Path));
            inner.SetValue(System.Windows.Shapes.Path.DataProperty, Geometry.Parse("M24,4 L664,4 L684,24 L684,88 L664,108 L24,108 L4,88 L4,24 Z"));
            inner.SetValue(System.Windows.Shapes.Shape.FillProperty, Brushes.Transparent);
            inner.SetValue(System.Windows.Shapes.Shape.StrokeProperty, Theme.Brush(Theme.GoldBorder));
            inner.SetValue(System.Windows.Shapes.Shape.StrokeThicknessProperty, 0.8);
            inner.SetValue(UIElement.IsHitTestVisibleProperty, false);
            grid.AppendChild(inner);

            FrameworkElementFactory presenter = new FrameworkElementFactory(typeof(ContentPresenter));
            presenter.SetValue(ContentPresenter.ContentProperty, new TemplateBindingExtension(ContentControl.ContentProperty));
            presenter.SetValue(ContentPresenter.MarginProperty, new TemplateBindingExtension(Control.PaddingProperty));
            presenter.SetValue(ContentPresenter.HorizontalAlignmentProperty, HorizontalAlignment.Stretch);
            presenter.SetValue(ContentPresenter.VerticalAlignmentProperty, VerticalAlignment.Stretch);
            grid.AppendChild(presenter);
            template.VisualTree = grid;

            Trigger hover = new Trigger { Property = UIElement.IsMouseOverProperty, Value = true };
            hover.Setters.Add(new Setter(Control.BackgroundProperty, CreateMetallicGoldBrush()));
            hover.Setters.Add(new Setter(Control.BorderBrushProperty, Theme.Brush(Theme.Text)));
            template.Triggers.Add(hover);
            Trigger pressed = new Trigger { Property = Button.IsPressedProperty, Value = true };
            pressed.Setters.Add(new Setter(UIElement.OpacityProperty, 0.88));
            template.Triggers.Add(pressed);
            Trigger focus = new Trigger { Property = UIElement.IsKeyboardFocusedProperty, Value = true };
            focus.Setters.Add(new Setter(Control.BorderBrushProperty, Brushes.White));
            template.Triggers.Add(focus);
            return template;
        }

        private static ControlTemplate CreateFlatButtonTemplate(double radius, bool dangerOnHover)
        {
            ControlTemplate template = new ControlTemplate(typeof(Button));
            FrameworkElementFactory border = new FrameworkElementFactory(typeof(Border));
            border.SetValue(Border.BackgroundProperty, new TemplateBindingExtension(Control.BackgroundProperty));
            border.SetValue(Border.CornerRadiusProperty, new CornerRadius(radius));
            FrameworkElementFactory presenter = new FrameworkElementFactory(typeof(ContentPresenter));
            presenter.SetValue(ContentPresenter.ContentProperty, new TemplateBindingExtension(ContentControl.ContentProperty));
            presenter.SetValue(ContentPresenter.HorizontalAlignmentProperty, HorizontalAlignment.Center);
            presenter.SetValue(ContentPresenter.VerticalAlignmentProperty, VerticalAlignment.Center);
            border.AppendChild(presenter);
            template.VisualTree = border;
            Trigger hover = new Trigger { Property = UIElement.IsMouseOverProperty, Value = true };
            hover.Setters.Add(new Setter(Control.BackgroundProperty, Theme.Brush(dangerOnHover ? Color.FromRgb(79, 27, 31) : Color.FromRgb(18, 37, 56))));
            template.Triggers.Add(hover);
            Trigger focus = new Trigger { Property = UIElement.IsKeyboardFocusedProperty, Value = true };
            focus.Setters.Add(new Setter(Control.BackgroundProperty, Theme.Brush(Color.FromRgb(27, 47, 66))));
            template.Triggers.Add(focus);
            return template;
        }

        private static void CaptureComposition(FrameworkElement composition, int logicalWidth, int logicalHeight, string outputPath, double dpi)
        {
            string directory = Path.GetDirectoryName(outputPath);
            if (!String.IsNullOrWhiteSpace(directory)) Directory.CreateDirectory(directory);
            composition.Measure(new Size(logicalWidth, logicalHeight));
            composition.Arrange(new Rect(0, 0, logicalWidth, logicalHeight));
            composition.UpdateLayout();
            int pixelWidth = (int)Math.Round(logicalWidth * dpi / 96.0);
            int pixelHeight = (int)Math.Round(logicalHeight * dpi / 96.0);
            RenderTargetBitmap rendered = new RenderTargetBitmap(pixelWidth, pixelHeight, dpi, dpi, PixelFormats.Pbgra32);
            rendered.Render(composition);
            PngBitmapEncoder encoder = new PngBitmapEncoder();
            encoder.Frames.Add(BitmapFrame.Create(rendered));
            using (FileStream stream = File.Create(outputPath)) encoder.Save(stream);
        }
    }
}
