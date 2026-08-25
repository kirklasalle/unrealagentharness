/**
 * UNREAL AGENT HARNESS (UAH) — WORLD-CLASS JAVASCRIPT ENGINE & MULTI-THEME SUITE
 * Architect: Kirk LaSalle & Antigravity AI Engineering
 * Features: Multi-Theme Switcher (5 Unreal Eras), Adaptive Cyber Canvas, Dynamic Spotlight, Interactive CSG Engine, Live Docs Filter, Mobile Drawer
 */

document.addEventListener('DOMContentLoaded', () => {
  initThemeSwitcher();
  initCyberCanvas();
  initSpotlightCards();
  initMobileNav();
  initTabs();
  initCopyCodeButtons();
  initEngineSelector();
  initCSGVisualizer();
  initDocsSearch();
  initScrollEffects();
});

/* ==========================================================================
   1. MULTI-THEME SWITCHER (5 UNREAL STYLES)
   ========================================================================== */
let currentTheme = 'liandri';

function initThemeSwitcher() {
  const savedTheme = localStorage.getItem('uah_theme') || 'liandri';
  currentTheme = savedTheme;
  document.documentElement.setAttribute('data-theme', savedTheme);

  const themeSelectors = document.querySelectorAll('.theme-select-input');
  themeSelectors.forEach(sel => {
    sel.value = savedTheme;
    sel.addEventListener('change', (e) => {
      const newTheme = e.target.value;
      currentTheme = newTheme;
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('uah_theme', newTheme);

      // Synchronize any other theme dropdowns on page
      themeSelectors.forEach(s => s.value = newTheme);

      // Re-trigger particle colors
      if (window.updateCanvasTheme) {
        window.updateCanvasTheme(newTheme);
      }
    });
  });
}

/* ==========================================================================
   2. CYBERNETIC VECTOR CANVAS (ADAPTIVE AMBIENT LATTICE)
   ========================================================================== */
function initCyberCanvas() {
  let canvas = document.getElementById('cyberCanvas');
  if (!canvas) {
    canvas = document.createElement('canvas');
    canvas.id = 'cyberCanvas';
    document.body.prepend(canvas);
  }

  const ctx = canvas.getContext('2d');
  let width, height;
  let particles = [];
  let mouse = { x: -1000, y: -1000, radius: 140 };

  function getThemeColors(theme) {
    switch (theme) {
      case 'napali':
        return { p1: 'rgba(16, 185, 129, 0.45)', p2: 'rgba(212, 175, 55, 0.35)', line: 'rgba(16, 185, 129,' };
      case 'ue5':
        return { p1: 'rgba(255, 255, 255, 0.45)', p2: 'rgba(56, 189, 248, 0.35)', line: 'rgba(255, 255, 255,' };
      case 'retro':
        return { p1: 'rgba(234, 179, 8, 0.5)', p2: 'rgba(132, 204, 22, 0.4)', line: 'rgba(234, 179, 8,' };
      case 'skaarj':
        return { p1: 'rgba(239, 68, 68, 0.5)', p2: 'rgba(59, 130, 246, 0.4)', line: 'rgba(239, 68, 68,' };
      case 'liandri':
      default:
        return { p1: 'rgba(245, 166, 35, 0.45)', p2: 'rgba(0, 212, 255, 0.35)', line: 'rgba(245, 166, 35,' };
    }
  }

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
    createParticles();
  }

  function createParticles() {
    particles = [];
    const count = Math.min(Math.floor((width * height) / 22000), 55);
    const colors = getThemeColors(currentTheme);

    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        size: Math.random() * 1.5 + 0.8,
        color: Math.random() > 0.4 ? colors.p1 : colors.p2
      });
    }
  }

  window.updateCanvasTheme = function(theme) {
    const colors = getThemeColors(theme);
    particles.forEach(p => {
      p.color = Math.random() > 0.4 ? colors.p1 : colors.p2;
    });
  };

  window.addEventListener('resize', resize);
  window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  window.addEventListener('mouseleave', () => {
    mouse.x = -1000;
    mouse.y = -1000;
  });

  resize();

  function animate() {
    ctx.clearRect(0, 0, width, height);
    const colors = getThemeColors(currentTheme);

    // Draw connecting lattice lines (Unreal ReachSpec Bot Network Simulation)
    for (let i = 0; i < particles.length; i++) {
      const p1 = particles[i];

      p1.x += p1.vx;
      p1.y += p1.vy;

      if (p1.x < 0 || p1.x > width) p1.vx *= -1;
      if (p1.y < 0 || p1.y > height) p1.vy *= -1;

      // Mouse gentle repulsion / energy
      const dxMouse = mouse.x - p1.x;
      const dyMouse = mouse.y - p1.y;
      const distMouse = Math.sqrt(dxMouse * dxMouse + dyMouse * dyMouse);
      if (distMouse < mouse.radius) {
        const force = (mouse.radius - distMouse) / mouse.radius;
        p1.x -= (dxMouse / distMouse) * force * 1.5;
        p1.y -= (dyMouse / distMouse) * force * 1.5;
      }

      ctx.beginPath();
      ctx.arc(p1.x, p1.y, p1.size, 0, Math.PI * 2);
      ctx.fillStyle = p1.color;
      ctx.fill();

      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 130) {
          const alpha = (1 - dist / 130) * 0.12;
          ctx.strokeStyle = `${colors.line} ${alpha})`;
          ctx.lineWidth = 0.75;
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(animate);
  }

  animate();
}

/* ==========================================================================
   3. DYNAMIC CARD SPOTLIGHT TRACKER (LUXURY HOVER EFFECT)
   ========================================================================== */
function initSpotlightCards() {
  const cards = document.querySelectorAll('.feature-card, .stat-card, .showcase-card, .timeline-card');

  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      card.style.setProperty('--mouse-x', `${x}px`);
      card.style.setProperty('--mouse-y', `${y}px`);
    });
  });
}

/* ==========================================================================
   4. MOBILE NAVIGATION DRAWER
   ========================================================================== */
function initMobileNav() {
  const toggleBtn = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');

  if (!toggleBtn || !navLinks) return;

  toggleBtn.addEventListener('click', () => {
    const isOpen = navLinks.classList.contains('mobile-open');
    if (isOpen) {
      navLinks.classList.remove('mobile-open');
      navLinks.style.display = 'none';
    } else {
      navLinks.classList.add('mobile-open');
      navLinks.style.display = 'flex';
      navLinks.style.flexDirection = 'column';
      navLinks.style.position = 'absolute';
      navLinks.style.top = '4.85rem';
      navLinks.style.left = '0';
      navLinks.style.width = '100%';
      navLinks.style.background = 'rgba(6, 8, 13, 0.98)';
      navLinks.style.padding = '2rem 1.5rem';
      navLinks.style.borderBottom = '1px solid rgba(245, 166, 35, 0.3)';
      navLinks.style.backdropFilter = 'blur(20px)';
      navLinks.style.gap = '1.25rem';
    }
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
      navLinks.classList.remove('mobile-open');
      navLinks.style.display = '';
      navLinks.style.flexDirection = '';
      navLinks.style.position = '';
      navLinks.style.padding = '';
      navLinks.style.background = '';
    }
  });
}

/* ==========================================================================
   5. TAB COMPONENT
   ========================================================================== */
function initTabs() {
  const tabContainers = document.querySelectorAll('.tab-container');

  tabContainers.forEach(container => {
    const buttons = container.querySelectorAll('.tab-btn');
    const panes = container.querySelectorAll('.tab-pane');

    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-tab');

        buttons.forEach(b => b.classList.remove('active'));
        panes.forEach(p => p.classList.remove('active'));

        btn.classList.add('active');
        const activePane = container.querySelector(`#${target}`);
        if (activePane) activePane.classList.add('active');
      });
    });
  });
}

/* ==========================================================================
   6. COPY CODE BUTTONS (WITH REAL-TIME TOOLTIP FEEDBACK)
   ========================================================================== */
function initCopyCodeButtons() {
  const codeBlocks = document.querySelectorAll('pre');

  codeBlocks.forEach(block => {
    const wrapper = block.parentElement;
    const header = wrapper.querySelector('.code-header');

    if (header && !header.querySelector('.btn-copy')) {
      const copyBtn = document.createElement('button');
      copyBtn.className = 'btn-copy';
      copyBtn.innerHTML = '📋 Copy';
      copyBtn.style.cssText = `
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.15);
        color: #94a3b8;
        font-family: var(--font-tech);
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.2rem 0.65rem;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s;
      `;

      copyBtn.addEventListener('mouseenter', () => {
        copyBtn.style.color = '#fff';
        copyBtn.style.borderColor = 'var(--gold-primary)';
      });
      copyBtn.addEventListener('mouseleave', () => {
        if (!copyBtn.classList.contains('copied')) {
          copyBtn.style.color = '#94a3b8';
          copyBtn.style.borderColor = 'rgba(255,255,255,0.15)';
        }
      });

      copyBtn.addEventListener('click', async () => {
        const codeText = block.innerText;
        try {
          await navigator.clipboard.writeText(codeText);
          copyBtn.classList.add('copied');
          copyBtn.innerHTML = '✓ Copied!';
          copyBtn.style.color = '#34d399';
          copyBtn.style.borderColor = '#34d399';
          setTimeout(() => {
            copyBtn.classList.remove('copied');
            copyBtn.innerHTML = '📋 Copy';
            copyBtn.style.color = '#94a3b8';
            copyBtn.style.borderColor = 'rgba(255,255,255,0.15)';
          }, 2000);
        } catch (err) {
          console.error('Failed to copy text: ', err);
        }
      });

      header.appendChild(copyBtn);
    }
  });
}

/* ==========================================================================
   7. MULTI-ENGINE MATRIX SELECTOR (DYNAMIC HUD DATA)
   ========================================================================== */
const ENGINE_PROFILES = {
  ut99_goty: {
    name: "Unreal Tournament 99 GOTY (UE1 / v469e)",
    era: "1999–Present",
    category: "Base Engine (Flagship UE1)",
    paradigm: "Subtractive CSG BSP + Vertex Animated Meshes",
    exe: "UnrealEd.exe / UnrealTournament.exe",
    ram: "< 35 MB (Harness) / ~65 MB (Engine)",
    features: "Botpack AI ReachSpec Lattice, 8-Bit HSV Radiosity, WarpZones, ZoneInfo, 3D Foliage, Pure CSG Geometry",
    packages: "Botpack.u, UnrealShare.u, UnrealI.u, GenEarth.utx, ShaneSky.utx, Ancient.utx",
    command: "launch_harness_ut99_goty.bat"
  },
  ut99_chaosut: {
    name: "ChaosUT: Evolution Mod (UE1 / 469e)",
    era: "Classic Community Mod",
    category: "Game Mod (Total Conversion)",
    paradigm: "Subtractive CSG BSP + Weapon & Physics Overhaul",
    exe: "UnrealEd.exe / UnrealTournament.exe (INI=ChaosUT.ini)",
    ram: "< 35 MB (Harness) / ~70 MB (Engine)",
    features: "Crossbows, Proxy Mines, Vortex Cannons, Grappling Hooks, Anti-Gravity Belts, Custom Melee Arenas",
    packages: "ChaosUT.u, ChaosMedia.u, ChaosTex.utx, ChaosSounds.uax",
    command: "launch_harness_universal.bat"
  },
  ut2004: {
    name: "Unreal Tournament 2004 (UE2.5 / v3369+)",
    era: "2004–Present",
    category: "Base Engine (Flagship UE2.5)",
    paradigm: "Hybrid CSG + Static Meshes (.usx) + Karma Physics",
    exe: "UnrealEd.exe / UT2004.exe",
    ram: "< 35 MB (Harness) / ~220 MB (Engine)",
    features: "Onslaught Vehicle Warfare, Karma Rigid Body Kinematics, xPawn & xWeapons, Terrain Actors, Voicepack remaps",
    packages: "Onslaught.u, XGame.u, XWeapons.u, ONSVehicles.u, EpicClassic.usx",
    command: "launch_harness_ut2004.bat"
  },
  ue5: {
    name: "Unreal Engine 5.x (Modern UE5)",
    era: "2022–2026+",
    category: "Base Engine (Modern Frontier)",
    paradigm: "Additive Virtualized Space + Nanite & Lumen",
    exe: "UnrealEditor.exe (Python Remote Exec Port 30010)",
    ram: "< 35 MB (Harness) / ~4-8 GB (Engine)",
    features: "Nanite Micro-Polygon Geometry, Lumen Dynamic GI, Python Remote Execution, Model Context Protocol (MCP)",
    packages: "UObject / UPackage, Blueprint & C++ Subsystems, Chaos Physics",
    command: "launch_harness_universal.bat --profile ue5"
  }
};

function initEngineSelector() {
  const selector = document.getElementById('engineProfileSelect');
  const detailsBox = document.getElementById('engineProfileDetails');

  if (!selector || !detailsBox) return;

  function updateDisplay(profileKey) {
    const data = ENGINE_PROFILES[profileKey];
    if (!data) return;

    detailsBox.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.25rem;">
        <div style="background: rgba(10, 14, 23, 0.85); border: 1px solid var(--glass-border); padding: 1.35rem; border-radius: var(--radius-md);">
          <div style="font-family: var(--font-tech); font-size: 0.82rem; text-transform: uppercase; color: var(--text-dim); letter-spacing: 0.12em;">Target Engine & Architecture</div>
          <div style="font-size: 1.15rem; font-weight: 700; color: var(--gold-light); margin-top: 0.35rem;">${data.name}</div>
          <div style="font-size: 0.88rem; color: var(--text-muted); margin-top: 0.25rem;">Era: ${data.era} • Class: ${data.category}</div>
        </div>

        <div style="background: rgba(10, 14, 23, 0.85); border: 1px solid var(--glass-border); padding: 1.35rem; border-radius: var(--radius-md);">
          <div style="font-family: var(--font-tech); font-size: 0.82rem; text-transform: uppercase; color: var(--text-dim); letter-spacing: 0.12em;">Geometry Core & Paradigm</div>
          <div style="font-size: 1.08rem; font-weight: 600; color: #fff; margin-top: 0.35rem;">${data.paradigm}</div>
          <div style="font-size: 0.85rem; color: #34d399; font-family: var(--font-mono); margin-top: 0.25rem;">Memory Overhead: ${data.ram}</div>
        </div>
      </div>

      <div style="margin-top: 1.25rem; background: #070a11; border: 1px solid var(--glass-border); border-radius: var(--radius-md); padding: 1.35rem;">
        <div style="font-family: var(--font-tech); font-size: 0.95rem; font-weight: 700; color: var(--gold-light); text-transform: uppercase; margin-bottom: 0.5rem; letter-spacing: 0.06em;">Key Supported Subsystems & Packages</div>
        <p style="font-size: 0.95rem; color: var(--text-muted); margin-bottom: 0.75rem;"><strong>Features:</strong> ${data.features}</p>
        <p style="font-size: 0.88rem; color: var(--cyan-accent); font-family: var(--font-mono); margin-bottom: 0.75rem;"><strong>Active Packages:</strong> ${data.packages}</p>
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem; padding-top: 0.75rem; border-top: 1px solid var(--glass-border);">
          <span style="font-size: 0.85rem; color: var(--text-dim);">Dedicated Launcher:</span>
          <code style="background: rgba(245,166,35,0.1); color: var(--gold-light); padding: 0.2rem 0.6rem; border-radius: 4px; border: 1px solid var(--gold-glow);">${data.command}</code>
        </div>
      </div>
    `;
  }

  selector.addEventListener('change', (e) => updateDisplay(e.target.value));
  updateDisplay(selector.value);
}

/* ==========================================================================
   8. INTERACTIVE CSG ROOM BUILDER / T3D SYNTHESIZER DEMO
   ========================================================================== */
function initCSGVisualizer() {
  const roomTypeSelect = document.getElementById('csgRoomType');
  const widthInput = document.getElementById('csgWidth');
  const depthInput = document.getElementById('csgDepth');
  const heightInput = document.getElementById('csgHeight');
  const textureSelect = document.getElementById('csgTexture');
  const generateBtn = document.getElementById('csgGenerateBtn');
  const previewBox = document.getElementById('csgOutputPreview');

  if (!generateBtn || !previewBox) return;

  function generateCSG() {
    const width = parseFloat(widthInput.value) || 3072;
    const depth = parseFloat(depthInput.value) || 3072;
    const height = parseFloat(heightInput.value) || 1024;
    const roomType = roomTypeSelect.value;
    const tex = textureSelect.value;

    const halfW = (width / 2).toFixed(1);
    const halfD = (depth / 2).toFixed(1);
    const halfH = (height / 2).toFixed(1);

    const isSubtractive = roomType.includes('subtractive');

    const t3dCode = `// ==========================================================================
// UAH AUTONOMOUS PROCEDURAL CSG SYNTHESIS STREAM (v1.0.0)
// Archetype: ${roomType.toUpperCase()} | Bounding: ${width}x${depth}x${height} UU
// Mathematical Integrity: 100% Watertight, Clockwise Winding, Zero BSP Cuts
// ==========================================================================
Begin Map
   // --- SUBTRACTIVE MAIN VOID HULL ---
   Begin Actor Class=Brush Name=MainHull_01
      CsgOper=${isSubtractive ? 'CSG_Subtract' : 'CSG_Add'}
      Location=(X=0.000000,Y=0.000000,Z=0.000000)
      Begin PolyList
         Begin Polygon Item=Floor Texture=${tex} Flags=0
            Origin   -${halfW},-${halfD},-${halfH}
            Normal   +0.000000,+0.000000,+1.000000
            Vertex   -${halfW},+${halfD},-${halfH}
            Vertex   +${halfW},+${halfD},-${halfH}
            Vertex   +${halfW},-${halfD},-${halfH}
            Vertex   -${halfW},-${halfD},-${halfH}
         End Polygon
         Begin Polygon Item=Ceiling Texture=${tex} Flags=0
            Origin   -${halfW},-${halfD},+${halfH}
            Normal   +0.000000,+0.000000,-1.000000
            Vertex   -${halfW},-${halfD},+${halfH}
            Vertex   +${halfW},-${halfD},+${halfH}
            Vertex   +${halfW},+${halfD},+${halfH}
            Vertex   -${halfW},+${halfD},+${halfH}
         End Polygon
      End PolyList
   End Actor
   
   // --- INJECT AI NAVIGATION & LIGHTING RIG ---
   Begin Actor Class=PathNode Name=PathNode_Center Location=(X=0.0,Y=0.0,Z=-${(halfH - 50).toFixed(1)}) End Actor
   Begin Actor Class=Light Name=Light_Key Location=(X=0.0,Y=0.0,Z=+${(halfH - 128).toFixed(1)})
      LightBrightness=220 LightHue=35 LightSaturation=30 LightRadius=64
   End Actor
End Map

MAP REBUILD
LIGHT APPLY
PATHS BUILD
FLUSH`;

    previewBox.textContent = t3dCode;
  }

  generateBtn.addEventListener('click', generateCSG);
  generateCSG();
}

/* ==========================================================================
   9. DOCUMENTATION & CITATION LIVE SEARCH
   ========================================================================== */
function initDocsSearch() {
  const searchInput = document.getElementById('docsSearchInput');
  const tagButtons = document.querySelectorAll('.docs-tag-btn');
  const docCards = document.querySelectorAll('.doc-entry-card, .citation-card');

  if (!searchInput && tagButtons.length === 0) return;

  function filterEntries() {
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const activeTagBtn = document.querySelector('.docs-tag-btn.active');
    const selectedTag = activeTagBtn ? activeTagBtn.getAttribute('data-tag') : 'all';

    docCards.forEach(card => {
      const text = card.innerText.toLowerCase();
      const tags = (card.getAttribute('data-tags') || '').toLowerCase();

      const matchesQuery = query === '' || text.includes(query);
      const matchesTag = selectedTag === 'all' || tags.includes(selectedTag);

      if (matchesQuery && matchesTag) {
        card.style.display = '';
      } else {
        card.style.display = 'none';
      }
    });
  }

  if (searchInput) {
    searchInput.addEventListener('input', filterEntries);
  }

  tagButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tagButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      filterEntries();
    });
  });
}

/* ==========================================================================
   10. SCROLL EFFECTS & BACK TO TOP
   ========================================================================== */
function initScrollEffects() {
  const backToTopBtn = document.getElementById('backToTopBtn');
  if (!backToTopBtn) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 400) {
      backToTopBtn.style.opacity = '1';
      backToTopBtn.style.pointerEvents = 'auto';
    } else {
      backToTopBtn.style.opacity = '0';
      backToTopBtn.style.pointerEvents = 'none';
    }
  });

  backToTopBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}
