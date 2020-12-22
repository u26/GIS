PImage img;

float R,G,B = 0;
int tx_size = 24;
int ls = 8;

void setup() {
  
  size(1024, 1024);
  //img = loadImage( "tile_fuji.png" );
  img = loadImage( "12_3626_1617.png" );
  //size( img.width, img.height );
  textSize(tx_size);
}

void draw() {
  
  background(200);
  image( img, 0, 0 );
 
  text(R, 512, tx_size);
  text(G, 512, tx_size*2+ls);
  text(B, 512, tx_size*3+ls*2);
  
  float h = pow(2,16)*R + pow(2,8)*G + B;
  text(h, 512, tx_size*4+ls*3);

}

void mousePressed() {
  
  //int idx = mouseX + mouseY * img.width;
  color c = img.get(mouseX, mouseY);
  
  R = red( c );
  G = green( c );
  B = blue( c );
}
    
