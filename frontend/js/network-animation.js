/**
 * TrueMesh - Network Animation
 * Animated particle network background
 */

class NetworkAnimation {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.particleCount = 100;
        this.connectionDistance = 150;
        this.mouse = { x: null, y: null, radius: 200 };
        
        this.init();
    }
    
    init() {
        this.resizeCanvas();
        this.createParticles();
        this.setupEventListeners();
        this.animate();
    }
    
    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    createParticles() {
        this.particles = [];
        for (let i = 0; i < this.particleCount; i++) {
            this.particles.push(new Particle(this.canvas));
        }
    }
    
    setupEventListeners() {
        window.addEventListener('resize', () => {
            this.resizeCanvas();
            this.createParticles();
        });
        
        this.canvas.addEventListener('mousemove', (e) => {
            this.mouse.x = e.x;
            this.mouse.y = e.y;
        });
        
        this.canvas.addEventListener('mouseleave', () => {
            this.mouse.x = null;
            this.mouse.y = null;
        });
    }
    
    connectParticles() {
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < this.connectionDistance) {
                    const opacity = 1 - (distance / this.connectionDistance);
                    
                    this.ctx.strokeStyle = `rgba(0, 217, 255, ${opacity * 0.3})`;
                    this.ctx.lineWidth = 1;
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    this.ctx.stroke();
                }
            }
            
            // Connect to mouse
            if (this.mouse.x !== null) {
                const dx = this.particles[i].x - this.mouse.x;
                const dy = this.particles[i].y - this.mouse.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < this.mouse.radius) {
                    const opacity = 1 - (distance / this.mouse.radius);
                    
                    this.ctx.strokeStyle = `rgba(112, 0, 255, ${opacity * 0.6})`;
                    this.ctx.lineWidth = 2;
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.mouse.x, this.mouse.y);
                    this.ctx.stroke();
                    
                    // Push particles away from mouse
                    const force = (this.mouse.radius - distance) / this.mouse.radius;
                    const angle = Math.atan2(dy, dx);
                    this.particles[i].vx += Math.cos(angle) * force * 0.5;
                    this.particles[i].vy += Math.sin(angle) * force * 0.5;
                }
            }
        }
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Update and draw particles
        this.particles.forEach(particle => {
            particle.update();
            particle.draw(this.ctx);
        });
        
        // Draw connections
        this.connectParticles();
        
        requestAnimationFrame(() => this.animate());
    }
}

class Particle {
    constructor(canvas) {
        this.canvas = canvas;
        this.reset();
    }
    
    reset() {
        this.x = Math.random() * this.canvas.width;
        this.y = Math.random() * this.canvas.height;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = (Math.random() - 0.5) * 0.5;
        this.radius = Math.random() * 2 + 1;
        this.opacity = Math.random() * 0.5 + 0.3;
    }
    
    update() {
        this.x += this.vx;
        this.y += this.vy;
        
        // Bounce off edges
        if (this.x < 0 || this.x > this.canvas.width) {
            this.vx *= -1;
            this.x = Math.max(0, Math.min(this.canvas.width, this.x));
        }
        
        if (this.y < 0 || this.y > this.canvas.height) {
            this.vy *= -1;
            this.y = Math.max(0, Math.min(this.canvas.height, this.y));
        }
        
        // Add slight friction
        this.vx *= 0.99;
        this.vy *= 0.99;
        
        // Ensure minimum velocity
        if (Math.abs(this.vx) < 0.1) this.vx = (Math.random() - 0.5) * 0.5;
        if (Math.abs(this.vy) < 0.1) this.vy = (Math.random() - 0.5) * 0.5;
    }
    
    draw(ctx) {
        // Draw particle
        ctx.fillStyle = `rgba(0, 217, 255, ${this.opacity})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw glow
        const gradient = ctx.createRadialGradient(
            this.x, this.y, 0,
            this.x, this.y, this.radius * 3
        );
        gradient.addColorStop(0, `rgba(0, 217, 255, ${this.opacity * 0.5})`);
        gradient.addColorStop(1, 'rgba(0, 217, 255, 0)');
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius * 3, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Alternative animation styles
class MatrixRain {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
        this.fontSize = 14;
        this.columns = 0;
        this.drops = [];
        
        this.init();
    }
    
    init() {
        this.resizeCanvas();
        this.setupEventListeners();
        this.animate();
    }
    
    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.columns = Math.floor(this.canvas.width / this.fontSize);
        this.drops = Array(this.columns).fill(1);
    }
    
    setupEventListeners() {
        window.addEventListener('resize', () => this.resizeCanvas());
    }
    
    animate() {
        this.ctx.fillStyle = 'rgba(10, 14, 39, 0.05)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = '#00d9ff';
        this.ctx.font = `${this.fontSize}px monospace`;
        
        for (let i = 0; i < this.drops.length; i++) {
            const char = this.chars[Math.floor(Math.random() * this.chars.length)];
            const x = i * this.fontSize;
            const y = this.drops[i] * this.fontSize;
            
            this.ctx.fillText(char, x, y);
            
            if (y > this.canvas.height && Math.random() > 0.975) {
                this.drops[i] = 0;
            }
            
            this.drops[i]++;
        }
        
        requestAnimationFrame(() => this.animate());
    }
}

class WaveAnimation {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.waves = [];
        this.waveCount = 3;
        this.time = 0;
        
        this.init();
    }
    
    init() {
        this.resizeCanvas();
        this.createWaves();
        this.setupEventListeners();
        this.animate();
    }
    
    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    createWaves() {
        this.waves = [];
        for (let i = 0; i < this.waveCount; i++) {
            this.waves.push({
                amplitude: 30 + i * 20,
                frequency: 0.002 - i * 0.0005,
                phase: i * Math.PI / 2,
                speed: 0.02 + i * 0.01,
                opacity: 0.3 - i * 0.08,
                color: `rgba(0, 217, 255, ${0.3 - i * 0.08})`
            });
        }
    }
    
    setupEventListeners() {
        window.addEventListener('resize', () => {
            this.resizeCanvas();
            this.createWaves();
        });
    }
    
    drawWave(wave) {
        this.ctx.beginPath();
        this.ctx.moveTo(0, this.canvas.height / 2);
        
        for (let x = 0; x < this.canvas.width; x++) {
            const y = this.canvas.height / 2 + 
                      Math.sin(x * wave.frequency + this.time * wave.speed + wave.phase) * 
                      wave.amplitude;
            this.ctx.lineTo(x, y);
        }
        
        this.ctx.strokeStyle = wave.color;
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.waves.forEach(wave => this.drawWave(wave));
        
        this.time += 0.1;
        
        requestAnimationFrame(() => this.animate());
    }
}

// Initialize network animation on page load
document.addEventListener('DOMContentLoaded', () => {
    // Default: Network animation
    new NetworkAnimation('networkCanvas');
    
    // Uncomment for alternative animations:
    // new MatrixRain('networkCanvas');
    // new WaveAnimation('networkCanvas');
});

// Export for use in other scripts
window.NetworkAnimation = NetworkAnimation;
window.MatrixRain = MatrixRain;
window.WaveAnimation = WaveAnimation;
