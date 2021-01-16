#include <fcntl.h>    /* For O_RDWR */
#include <unistd.h>   /* For open(), creat() */
#include <termios.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <thread>
#include <chrono>

using namespace std;
int USB;
fd_set read_fds, write_fds, except_fds;
struct timeval timeout;
int HUMAN=0;

int initUSB(char* usbport){
    USB = open( usbport, O_RDWR | O_NOCTTY); 

    struct termios tty;
    struct termios tty_old;
    memset (&tty, 0, sizeof tty);

    /* Error Handling */
    if ( tcgetattr ( USB, &tty ) != 0 ) {
        printf("ERROR HERE\n");
       std::cout << "Error " << errno << " from tcgetattr: " << strerror(errno) << std::endl;
    }

    /* Save old tty parameters */
    tty_old = tty;

    /* Set Baud Rate */
    cfsetospeed (&tty, (speed_t)B57600);
    cfsetispeed (&tty, (speed_t)B57600);

    /* Setting other Port Stuff */
    tty.c_cflag     &=  ~PARENB;            // Make 8n1
    tty.c_cflag     &=  ~CSTOPB;
    tty.c_cflag     &=  ~CSIZE;
    tty.c_cflag     |=  CS8;

    tty.c_cflag     &=  ~CRTSCTS;           // no flow control
    tty.c_lflag &= ~ICANON; /* Set non-canonical mode */
    tty.c_cc[VMIN]   =  0;                  // read doesn't block
    tty.c_cc[VTIME]  =  0;                  // 0.5 seconds read timeout
    tty.c_cflag     |=  CREAD | CLOCAL;     // turn on READ & ignore ctrl lines

    /* Make raw */
    cfmakeraw(&tty);
    
    /* Flush Port, then applies attributes */
    tcflush( USB, TCIFLUSH );
    if ( tcsetattr ( USB, TCSANOW, &tty ) != 0) {
        printf("ERROR HERE 1\n");
        std::cout << "Error " << errno << " from tcsetattr" << std::endl;
        return 1;
    }
    unsigned char cmd[] = "START";
    int n_written = 0, spot = 0;
    int a = 2;
    void* aa = &a;   
    n_written = write( USB, aa, 1 );

    n_written = write( USB, &cmd[0], 1 );
    n_written = write( USB, &cmd[1], 1 );
    n_written = write( USB, &cmd[2], 1 );
    n_written = write( USB, &cmd[3], 1 );
    n_written = write( USB, &cmd[4], 1 );

    int b = 3;
    void* bb = &b;

    n_written = write( USB, bb, 1 );
    // Initialize file descriptor sets
    
    FD_ZERO(&read_fds);
    FD_ZERO(&write_fds);
    FD_ZERO(&except_fds);
    FD_SET(USB, &read_fds);
    // Set timeout to 1.0 seconds
   
    timeout.tv_sec = 1;
    timeout.tv_usec = 0;    
    
    return USB;
}

int find_max(int *data, int count){
    int max=data[0];
    for(int i=0;i<count;i++){
        if(max<data[i]){
            max=data[i];
        }
    }
    return max;

}

int find_min(int *data, int count){
    int min=data[0];
    for(int i=0;i<count;i++){
        if(min>data[i]){
            min=data[i];
        }
    }
    return min;

}

int concat(int a, int b, int c, int d) 
{ 
  
    // Convert both the integers to string 
    string s1 = to_string(a); 
    string s2 = to_string(b);
    string s3 = to_string(c); 
    string s4 = to_string(d);  
  
    // Concatenate both strings 
    string s = s1 + s2 + s3 + s4; 
  
    // Convert the concatenated string 
    // to integer 
    int e = stoi(s); 
  
    // return the formed integer 
    return e; 
} 

int main(int argc, char* argv[]){
    char* usbport = argv[1];
    USB = initUSB(usbport);
    FILE *pFile;
    FILE *oFile;
    pFile = fopen("rawdata.txt","w"); 
    oFile = fopen("output3.csv", "w");
    int count=0;
    int c=0;    
    int detect=0;
    int state=1;
    int detected=0;

    string filename="rawdata.txt";
    string output_filename="output3.csv";
    int *a=new int[6];
    int *arr=new int[2000];
    int *result=new int [310];


    ifstream openFile(filename.data());
    

    while(1){   
        int n = 0;
        char buf[1];
        int temp = select(USB + 1, &read_fds, &write_fds, &except_fds, &timeout);

        if (temp == 1)
        {
            // fd is ready for reading
            n = read( USB, &buf, 1 );
            int b = buf[0]-'0';
            count++;
            arr[count]=b;
            
            detected=0;
            
            if(count==2000)
            {
                for(int i=0;i<2000;i++){
                    if(arr[i]==-46)
                    {
                        if(arr[i+5]==-45)
                        {
                            a[0]=arr[i+1];
                            a[1]=arr[i+2];
                            a[2]=arr[i+3];
                            a[3]=arr[i+4];
                            int out=concat(a[0],a[1],a[2],a[3]);        
                            result[c++]=out;
                            if(c==300)
                            {
                                int maximum=find_max(result, 300);
                                int minimum=find_min(result, 300);     
                                int re=maximum-minimum;
                                
                                if(re>=400){
                                    detected=1;
                                }
                                
                                if(detected==0){
                                }
                                else {
                                    printf("Human Is Detected\n");
                                    popen("echo 1 > /sys/class/gpio/gpio113/value", "r");
                                    state=1;
                                    detected=0;
                                }
                            c=0;
                            }
                        }
                    }
                }
            count=0;
            }
        }
        else{
            count++;
            
            close(USB);
            USB = initUSB(usbport); 
        }
    }      
}

