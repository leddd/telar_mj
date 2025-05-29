int numTeclas = 24;
Letra[] letras = new Letra[numTeclas];

void setup() {
  size(1000, 600);
  for (int i = 0; i < numTeclas; i++) {
    letras[i] = new Letra(i);
  }
  background(255);
  smooth();
}

void draw() {
  background(255);
  
  // Línea divisoria central
  stroke(200);
  strokeWeight(2);
  line(width/2, 0, width/2, height);
  
  // Texto etiquetas
  fill(150);
  noStroke();
  textAlign(CENTER, CENTER);
  textSize(16);
  text("Zona Izquierda", width/4, 30);
  text("Zona Derecha", 3*width/4, 30);
  
  for (Letra l : letras) {
    l.actualizar();
  }
}

void keyPressed() {
  int idx = -1;
  
  // Mapear teclas 1-9, a-l, z-x a índices 0-23
  if (key >= '1' && key <= '9') idx = key - '1'; 
  else if (key >= 'a' && key <= 'l') idx = 9 + (key - 'a'); 
  else if (key >= 'z' && key <= 'x') idx = 21 + (key - 'z');
  
  if (idx >= 0 && idx < letras.length) {
    letras[idx].activar();
  }
}

// Clase para cada tecla/letra
class Letra {
  int idx;
  PVector basePos;
  ArrayList<PVector[]> trazosOriginales; // curvas base
  ArrayList<PVector[]> trazosAnimados;   // curvas con movimiento orgánico
  int duracionAnim = 120; // frames (2 segundos a 60fps)
  int frameStart = -duracionAnim; // iniciar desactivado
  
  Letra(int idx) {
    this.idx = idx;
    float baseX;
    if (idx < 12) {
      // Primera mitad del canvas, 12 teclas izquierda
      baseX = map(idx, 0, 11, 20, width/2 - 20);
    } else {
      // Segunda mitad del canvas, 12 teclas derecha
      baseX = map(idx, 12, 23, width/2 + 20, width - 20);
    }
    float baseY = height / 2;
    basePos = new PVector(baseX, baseY);
    trazosOriginales = new ArrayList<PVector[]>();
    trazosAnimados = new ArrayList<PVector[]>();
  }
  
  void crearAnimacion() {
    trazosOriginales.clear();
    trazosAnimados.clear();
    int numTrazos = 3; // 3 curvas por tecla
    for (int i = 0; i < numTrazos; i++) {
      float ampl = random(40, 120);
      PVector[] curvaBase = new PVector[4];
      for (int j = 0; j < 4; j++) {
        float x = basePos.x + random(-ampl, ampl);
        float y = basePos.y + random(-ampl, ampl);
        curvaBase[j] = new PVector(x, y);
      }
      trazosOriginales.add(curvaBase);
      PVector[] copia = new PVector[4];
      for (int k = 0; k < 4; k++) {
        copia[k] = curvaBase[k].copy();
      }
      trazosAnimados.add(copia);
    }
  }
  
  void activar() {
    crearAnimacion();
    frameStart = frameCount;
  }
  
  void actualizar() {
    int framesPassed = frameCount - frameStart;
    if (framesPassed < 0 || framesPassed > duracionAnim) return;
    
    // Calcular alpha para fade in y fade out
    float alpha = 255;
    float pct = framesPassed / float(duracionAnim);
    if (pct < 0.25) {
      alpha = map(pct, 0, 0.25, 0, 255);
    } else if (pct > 0.75) {
      alpha = map(pct, 0.75, 1, 255, 0);
    }
    
    stroke(0, alpha);
    noFill();
    strokeWeight(2);
    
    for (int i = 0; i < trazosOriginales.size(); i++) {
      PVector[] original = trazosOriginales.get(i);
      PVector[] animado = trazosAnimados.get(i);
      for (int j = 0; j < 4; j++) {
        animado[j].x = original[j].x + 5 * sin(radians(frameCount * 5 + idx * 20 + j * 50));
        animado[j].y = original[j].y + 5 * cos(radians(frameCount * 7 + idx * 15 + j * 30));
      }
      beginShape();
      vertex(animado[0].x, animado[0].y);
      bezierVertex(animado[1].x, animado[1].y, animado[2].x, animado[2].y, animado[3].x, animado[3].y);
      endShape();
    }
  }
}
