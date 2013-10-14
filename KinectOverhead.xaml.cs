using System;
using System.IO;
using System.Collections.Generic;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.DataVisualization.Charting;
using System.Windows.Data;
using System.Windows.Documents;
using System.Runtime.InteropServices;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using Microsoft.Research.Kinect.Nui;
using Emgu.CV;
using Emgu.CV.UI;
using Emgu.Util;
using Emgu.CV.Structure;




namespace KinectOverhead
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        #region MainWindow globalVariables

        // runtime object for kinect resources.
        Runtime nui = new Runtime() ;

        // Distance (in mm) of threshold
        const int THRESHOLD = 38; // if THRESHOLD <= zero, no display.
        
        // base frame number:
        const int BASEFRAME = 10;
        
        // accumulator for number of pixels processed.
        int pixelNumber = 0;

        // counter for frames TODO: short circuit (boolean method?) when not needed anymore?
        public static int frameCounter = 0;

        // base plane to compare frames against.
        public ImageFrame storedImageFrame = new ImageFrame() ;//new Byte[307200];  //320 * 240 * 4 (height*width*1emptyByte)

       // public ImageFrame capturedImageFrame = new ImageFrame();

        // Distance average for all pixels
        public int cumPixelDistance = 0;

        // frame number to save
        public int SAVE_FRAME = 310;

        #endregion

        public MainWindow()
        {
            InitializeComponent();
        }

        private void Window_Loaded(object sender, RoutedEventArgs e)
        {         
            //UseDepthAndPlayerIndex
            nui.Initialize(RuntimeOptions.UseDepth);

            //register for event
            nui.DepthFrameReady += new EventHandler<ImageFrameReadyEventArgs>(nui_DepthFrameReady);

            //DepthAndPlayerIndex ImageType
            nui.DepthStream.Open(ImageStreamType.Depth, 2, ImageResolution.Resolution320x240,
                ImageType.Depth);
        }

        void nui_DepthFrameReady(object sender, ImageFrameReadyEventArgs e)
        {
                // holds color-coded depth map
                byte[] ColoredBytes = GenerateColoredBytes(e.ImageFrame);
                           
                //create an image based on returned colors
                PlanarImage image = e.ImageFrame.Image;
                image1.Source = BitmapSource.Create(image.Width, image.Height, 96, 96, PixelFormats.Bgr32, null,
               ColoredBytes, image.Width * PixelFormats.Bgr32.BitsPerPixel / 8);
                           

        }

        private byte[] GenerateColoredBytes(ImageFrame imageFrame)
        {
            int height = imageFrame.Image.Height;
            int width = imageFrame.Image.Width;
            
            cumPixelDistance = 0;
            pixelNumber = 0;
            
            //Depth data for each pixel
            Byte[] depthData = imageFrame.Image.Bits;
            Byte[] storedDepthData = storedImageFrame.Image.Bits;

            //colorFrame contains color information for all pixels in image
            //Height x Width x 4 (Red, Green, Blue, empty byte)
            Byte[] colorFrame = new Byte[imageFrame.Image.Height * imageFrame.Image.Width * 4];

            //Bgr32  - Blue, Green, Red, empty byte
            //Bgra32 - Blue, Green, Red, transparency 
            //You must set transparency for Bgra as .NET defaults a byte to 0 = fully transparent

            //hardcoded locations to Blue, Green, Red (BGR) index positions       
            const int BlueIndex = 0;
            const int GreenIndex = 1;
            const int RedIndex = 2;
                       
            var depthIndex = 0;
            for (var y = 0; y < height; y++)
            {
                var heightOffset = y * width;

                for (var x = 0; x < width; x++)
                {

                    //var index = ((width - x - 1) + heightOffset) * 4; // for mirror image orientation(display)
                    var index = (x + heightOffset) * 4; // for normal image orientation(display)
                    
                    // get distance data from current pixel
                    var curDistance = (int)(depthData[depthIndex] | depthData[depthIndex + 1] << 8);
                    
                    // distance averaging computation
                    cumPixelDistance += curDistance;
                    pixelNumber++;

                    //var d1 = (int)(depthData[depthIndex]);
                    //var d2 = (int)(depthData[depthIndex]+1);
                    //d1 = d1 << 8;
                    //var curDistance = d1 + d2;
                                      
                    // wait until base frame is stored, then compare distances.
                    if (frameCounter > BASEFRAME)
                    {
                       // get distance for corresponding pixel in base frame.
                       var baseDistance = (int)(storedDepthData[depthIndex] | storedDepthData[depthIndex + 1] << 8);
                       
                       //var bd1 = (int)(storedDepthData[depthIndex]);
                       //var bd2 = (int)(storedDepthData[depthIndex] + 1);
                       //bd1 = bd1 << 8;
                       //var baseDistance = bd1 + bd2;
                                             
                       // if current pixel distance is closer, color.
                        if ( (baseDistance - curDistance) > THRESHOLD)
                        {
                            colorFrame[index + BlueIndex] = 0;
                            colorFrame[index + GreenIndex] = 0;
                            colorFrame[index + RedIndex] = 0;
                        }
                        else // color base area 
                        {
                            colorFrame[index + BlueIndex] = 255;
                            colorFrame[index + GreenIndex] = 255;
                            colorFrame[index + RedIndex] = 255;
                        }
                    }
                    //jump two bytes at a time, depth info two bytes long.
                    depthIndex += 2;
                }
            }

            if (frameCounter == BASEFRAME)
            {
                // capture depth data for base frame
                storedImageFrame = imageFrame;
            
                frameCounter++;
            }
           

            else // TODO: instead just increment once?;  both code paths need to have frameCounter incremented.
            {
                frameCounter++;
            }
            
            
            distanceLabel.Content = cumPixelDistance / pixelNumber;


            return colorFrame;
        }

            
        private void Window_Closed(object sender, EventArgs e)
        {
          
            //cleanup
            nui.Uninitialize(); 
        }

        
            







    }
    
}
