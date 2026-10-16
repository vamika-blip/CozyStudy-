// audio.js - Pure Web Audio API Sound Synthesizer
// Zero external mp3 dependencies, runs 100% offline

class SoundEngine {
  constructor() {
    this.ctx = null;
    this.ambientSource = null;
    this.ambientGain = null;
    this.isAmbientPlaying = false;
  }

  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioContext();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  // Soft ascending chime for session start
  playStartChime() {
    try {
      this.init();
      const now = this.ctx.currentTime;
      const notes = [523.25, 659.25, 783.99]; // C5, E5, G5
      notes.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, now + idx * 0.12);

        gain.gain.setValueAtTime(0, now + idx * 0.12);
        gain.gain.linearRampToValueAtTime(0.18, now + idx * 0.12 + 0.04);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.12 + 0.6);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now + idx * 0.12);
        osc.stop(now + idx * 0.12 + 0.65);
      });
    } catch (e) {
      console.warn('Audio playStartChime warning:', e);
    }
  }

  // Celebratory completion chime (C major arpeggio + bell)
  playCompletionChime() {
    try {
      this.init();
      const now = this.ctx.currentTime;
      const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
      notes.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, now + idx * 0.15);

        gain.gain.setValueAtTime(0, now + idx * 0.15);
        gain.gain.linearRampToValueAtTime(0.25, now + idx * 0.15 + 0.03);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + idx * 0.15 + 1.2);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now + idx * 0.15);
        osc.stop(now + idx * 0.15 + 1.3);
      });
    } catch (e) {
      console.warn('Audio playCompletionChime warning:', e);
    }
  }

  // Anti-cheat alert sound (soft warning ping)
  playWarningChime() {
    try {
      this.init();
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(329.63, now); // E4
      osc.frequency.exponentialRampToValueAtTime(220.00, now + 0.35); // A3

      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.45);
    } catch (e) {
      console.warn('Audio playWarningChime warning:', e);
    }
  }

  // Cute charm unlock chime (twinkle)
  playCharmChime() {
    try {
      this.init();
      const now = this.ctx.currentTime;
      const freqs = [880, 1174.66, 1318.51, 1760];
      freqs.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, now + idx * 0.08);

        gain.gain.setValueAtTime(0.15, now + idx * 0.08);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.08 + 0.5);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now + idx * 0.08);
        osc.stop(now + idx * 0.08 + 0.55);
      });
    } catch (e) {
      console.warn('Audio playCharmChime warning:', e);
    }
  }

  // Procedural lo-fi brown noise / rain generator
  startAmbientRain(volume = 0.25) {
    try {
      this.stopAmbient();
      this.init();

      const bufferSize = this.ctx.sampleRate * 2;
      const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const data = buffer.getChannelData(0);
      let lastOut = 0.0;

      // Brown noise formula (rain-like)
      for (let i = 0; i < bufferSize; i++) {
        const white = Math.random() * 2 - 1;
        data[i] = (lastOut + 0.02 * white) / 1.02;
        lastOut = data[i];
        data[i] *= 3.5;
      }

      this.ambientSource = this.ctx.createBufferSource();
      this.ambientSource.buffer = buffer;
      this.ambientSource.loop = true;

      // Lowpass filter to simulate gentle indoor rain
      const filter = this.ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(750, this.ctx.currentTime);

      this.ambientGain = this.ctx.createGain();
      this.ambientGain.gain.setValueAtTime(volume, this.ctx.currentTime);

      this.ambientSource.connect(filter);
      filter.connect(this.ambientGain);
      this.ambientGain.connect(this.ctx.destination);

      this.ambientSource.start();
      this.isAmbientPlaying = true;
    } catch (e) {
      console.warn('Audio startAmbientRain warning:', e);
    }
  }

  stopAmbient() {
    try {
      if (this.ambientSource) {
        this.ambientSource.stop();
        this.ambientSource.disconnect();
        this.ambientSource = null;
      }
      this.isAmbientPlaying = false;
    } catch (e) {
      console.warn('Audio stopAmbient warning:', e);
    }
  }
}

export const sound = new SoundEngine();
