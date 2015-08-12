#include "libuvc/libuvc.h"
#include <X11/Xlib.h>
#include <X11/keysym.h>
#include <stdio.h>
#include <unistd.h>
#include "stills2dv.h"
#include "x_lowlevel.h"




int winWidth=0;
int winHeight=0;
int camWidth=0;
int camHeight=0;
ImageWindow *iw=NULL;  
Display    *dis=NULL;

void initGlobals(void){
  camWidth=1280;
  camHeight=720;
  winWidth=1280;
  winHeight=720;
}

void checkevent(void){
  XEvent e;
  XSelectInput(dis, iw->window, ExposureMask);
         XNextEvent(dis, &e);
         switch  (e.type)
	   {
	        case Expose:
                 ExposeImageWindow(iw);
	        break;
/* 	        case KeyPress: */
/* 	            // Press "Q" to quit. */
/* 	            if(XLookupKeysym(&e.xkey, 0) == XK_q) */
/* 	                done = True; */
	        default:
	        break;
	    }
}

void showpart(unsigned char *data, int woffx, int woffy, int coffx, int coffy){
  unsigned long pixel;
  int x, y, idx;
  for (y=0;y<(winHeight/4);y++){
    for (x=0;x<(winWidth/4);x++){
      idx=(coffy+y)*camWidth;
      idx+=coffx+x;
      idx *=3;
      pixel=data[idx];
      pixel|=(unsigned int)(data[idx+1])<<8;
      pixel|=(unsigned int)(data[idx+1])<<16;
      pixel|=0xff000000;
      //printf("idx=%6d, pixel=%08X, offx=%d, offy=%d, x=%d, y=%d, h=%d, w=%d\n",idx, pixel, offx, offy, x,y,w,h);
      PutPixel(iw,woffx+x, woffy+y, pixel);
      if ((x==0)||(y==0)||(x== ((winWidth/4)-1))||(y==((winHeight/4)-1))) {
	PutPixel(iw, (winWidth/2)+(winWidth*(x+coffx)/(4*camWidth)), (winHeight/4)+(winHeight*(y+coffy)/(4*camHeight)), 0xff0000ff);
      }
    }
  }
}


void showthumbnail(unsigned char *data){
  unsigned long pixel;
  int x, y, cx, cy, idx;
  for (y=0;y<(winHeight/4);y++){
    for (x=0;x<(winWidth/4);x++){
      cx=(4*x*camWidth)/winWidth;
      cy=(4*y*camHeight)/winHeight;
      idx=3 * (cx+(cy*camWidth));
      pixel=data[idx];
      pixel|=(unsigned int)(data[idx+1])<<8;
      pixel|=(unsigned int)(data[idx+1])<<16;
      pixel|=0xff000000;
      //printf("idx=%6d, pixel=%08X, offx=%d, offy=%d, x=%d, y=%d, h=%d, w=%d\n",idx, pixel, offx, offy, x,y,w,h);
      PutPixel(iw,(winWidth/2)+x, (winHeight/4)+y, pixel);      
    }
  }
}

/* This callback function runs once per frame. Use it to perform any
 * quick processing you need, or have it put the frame into your application's
 * input queue. If this function takes too long, you'll start losing frames. */
void cb(uvc_frame_t *frame, void *ptr) {
  static int count=0;
  uvc_frame_t *bgr;
  uvc_error_t ret;
  while (count < 30 ) {
    count++;
    return;
  }
  
  /* We'll convert the image from YUV/JPEG to BGR, so allocate space */
  bgr = uvc_allocate_frame(frame->width * frame->height * 3);
  if (!bgr) {
    printf("unable to allocate bgr frame!");
    return;
  }  
  /* Do the BGR conversion */
  ret =uvc_mjpeg2rgb (frame, bgr);
  if (ret) {
    uvc_perror(ret, "uvc_mjpeg2bgr");
    uvc_free_frame(bgr);
    return;
  }
  //printf("showthumbnail\n");
  showthumbnail(bgr->data);
  showpart(bgr->data, winWidth/4, 0, camWidth/10, camHeight/10);
  showpart(bgr->data, 3*winWidth/4, 0, 9*camWidth/10 - winWidth/4, camHeight/10);
  showpart(bgr->data, winWidth/4, 3*winHeight/4, camWidth/10, 9*camHeight/10 - winHeight/4);
  showpart(bgr->data, 3*winWidth/4, 3*winHeight/4, 9*camWidth/10-winWidth/4, 9*camHeight/10-winHeight/4);
  showpart(bgr->data, winWidth/2, winHeight/2, camWidth/2-winWidth/8, camHeight/2-winHeight/8);
  showpart(bgr->data, winWidth/4, 3*winHeight/8, camWidth/3-winWidth/8, camHeight/2-winHeight/8);
  showpart(bgr->data, 3*winWidth/4, 3*winHeight/8, 2*camWidth/3-winWidth/8, camHeight/2-winHeight/8);


  //printf("checkevent\n");
  fflush(stdout);
  checkevent();
  //printf("SendExposeEvent\n");
  SendExposeEvent(iw);
  //  sprintf(fn, "%04d.data", count);
  //  out=fopen(fn, "wb");
  //  fwrite(bgr->data, 3 *  bgr->width, bgr->height, out);
  //  fclose(out);
  //  sprintf(fn, "%04d.head", count);
  //  out=fopen(fn, "wb");
  //  fwrite(frame, sizeof(uvc_frame_t), 1, out);
  //  fclose(out);
  
  /* Call a user function:
   *
   * my_type *my_obj = (*my_type) ptr;
   * my_user_function(ptr, bgr);
   * my_other_function(ptr, bgr->data, bgr->width, bgr->height);
   */

  /* Call a C++ method:
   *
   * my_type *my_obj = (*my_type) ptr;
   * my_obj->my_func(bgr);
   */

  /* Use opencv.highgui to display the image:
   * 
   * cvImg = cvCreateImageHeader(
   *     cvSize(bgr->width, bgr->height),
   *     IPL_DEPTH_8U,
   *     3);
   *
   * cvSetData(cvImg, bgr->data, bgr->width * 3); 
   *  
   * cvNamedWindow("Test", CV_WINDOW_AUTOSIZE);
   * cvShowImage("Test", cvImg);
   * cvWaitKey(10);
   *
   * cvReleaseImageHeader(&cvImg);
   */

  uvc_free_frame(bgr);
}

int main(int argc, char **argv) {
  uvc_context_t *ctx=NULL;
  uvc_device_t *dev=NULL;
  uvc_device_handle_t *devh=NULL;
  uvc_stream_ctrl_t ctrl;
  uvc_error_t res;  
  if (!dis)dis = XOpenDisplay(NULL);
  if (!dis) FatalError("Display could not be initialized.");
  initGlobals();
  if(!iw)iw = CreateDefaultImageWindow(dis, 1, 1, winWidth, winHeight);
  checkevent();
  SendExposeEvent(iw);
  
  
  /* Initialize a UVC service context. Libuvc will set up its own libusb
   * context. Replace NULL with a libusb_context pointer to run libuvc
   * from an existing libusb context. */
  res = uvc_init(&ctx, NULL);

  if (res < 0) {
    uvc_perror(res, "uvc_init");
    return res;
  }

  puts("UVC initialized");

  /* Locates the first attached UVC device, stores in dev */
  res = uvc_find_device(
      ctx, &dev,
      0, 0, NULL); /* filter devices: vendor_id, product_id, "serial_num" */

  if (res < 0) {
    uvc_perror(res, "uvc_find_device"); /* no devices found */
  } else {
    puts("Device found");

    /* Try to open the device: requires exclusive access */
    res = uvc_open(dev, &devh);

    if (res < 0) {
      uvc_perror(res, "uvc_open"); /* unable to open device */
    } else {
      puts("Device opened");

      /* Print out a message containing all the information that libuvc
       * knows about the device */
      uvc_print_diag(devh, stderr);

      /* Try to negotiate a 640x480 30 fps YUYV stream profile */
      res = uvc_get_stream_ctrl_format_size(
          devh, &ctrl, /* result stored in ctrl */
          UVC_FRAME_FORMAT_COMPRESSED, /* YUV 422, aka YUV 4:2:2. try _COMPRESSED */
          camWidth, camHeight, 30 /* width, height, fps */
      );

      /* Print out the result */
      uvc_print_stream_ctrl(&ctrl, stderr);

      if (res < 0) {
        uvc_perror(res, "get_mode"); /* device doesn't provide a matching stream */
      } else {
        /* Start the video stream. The library will call user function cb:
         *   cb(frame, (void*) 12345)
         */
        res = uvc_start_streaming(devh, &ctrl, cb, (void *)12345, 0);

        if (res < 0) {
          uvc_perror(res, "start_streaming"); /* unable to start stream */
        } else {
          puts("Streaming...");

          uvc_set_ae_mode(devh, 1); /* e.g., turn on auto exposure */

          while (1) {sleep(20);}

          /* End the stream. Blocks until last callback is serviced */
          uvc_stop_streaming(devh);
          puts("Done streaming.");
        }
      }

      /* Release our handle on the device */
      uvc_close(devh);
      puts("Device closed");
    }

    /* Release the device descriptor */
    uvc_unref_device(dev);
  }

  /* Close the UVC context. This closes and cleans up any existing device handles,
   * and it closes the libusb context if one was not provided. */
  uvc_exit(ctx);
  puts("UVC exited");

  return 0;
}

