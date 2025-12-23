import math

def hex_to_rgb(hex_color):
    """Hex (#RRGGBB) rengini RGB tuple'a (r, g, b) çevirir."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    """RGB tuple'ı Hex (#RRGGBB) rengine çevirir."""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb_color[0]), int(rgb_color[1]), int(rgb_color[2]))

def interpolate_color(start_hex, end_hex, progress):
    """
    İki renk arasında geçiş yapar.
    progress: 0.0 (başlangıç) ile 1.0 (bitiş) arasında bir değer.
    """
    start_rgb = hex_to_rgb(start_hex)
    end_rgb = hex_to_rgb(end_hex)
    
    r = start_rgb[0] + (end_rgb[0] - start_rgb[0]) * progress
    g = start_rgb[1] + (end_rgb[1] - start_rgb[1]) * progress
    b = start_rgb[2] + (end_rgb[2] - start_rgb[2]) * progress
    
    return rgb_to_hex((r, g, b))

def ease_out_quart(x):
    """Yumuşak bitiş hızı (Ease Out Quart)"""
    return 1 - pow(1 - x, 4)

def ease_in_out_sine(x):
    """Yumuşak başlangıç ve bitiş (Ease In Out Sine)"""
    return -(math.cos(math.pi * x) - 1) / 2

class AnimationController:
    """Widget animasyonlarını yöneten yardımcı sınıf"""
    
    @staticmethod
    def animate_color(widget, prop, start_color, end_color, duration=300, steps=20):
        """
        Bir widget'ın renk özelliğini (fg_color, hover_color vb.) animasyonla değiştirir.
        Tuple/List renkleri (Light/Dark mode) destekler.
        """
        delay = duration // steps
        
        # Renkleri normalize et (Tek string veya tuple)
        def parse_color(c):
            if isinstance(c, (list, tuple)) and len(c) > 0:
                return c
            return (c, c) if c else ("#FFFFFF", "#000000") # Fallback
            
        start_c = parse_color(start_color)
        end_c = parse_color(end_color)
        
        # Eğer tek string geldiyse ama öbürü tuple ise uyumlu hale getir
        if isinstance(start_color, str) and isinstance(end_color, (list, tuple)):
             start_c = (start_color, start_color)
        elif isinstance(end_color, str) and isinstance(start_color, (list, tuple)):
             end_c = (end_color, end_color)
        
        def step(current_step):
            try:
                if not widget.winfo_exists(): return
            except: return

            if current_step > steps:
                try: widget.configure(**{prop: end_color})
                except: pass
                return
            
            progress = current_step / steps
            eased_progress = ease_out_quart(progress)
            
            # Hem Light hem Dark için hesapla
            try:
                # Bazen renkler None veya garip formatta gelebilir, try-catch içinde yap
                r1 = interpolate_color(str(start_c[0]), str(end_c[0]), eased_progress)
                
                if len(start_c) > 1 and len(end_c) > 1:
                    r2 = interpolate_color(str(start_c[1]), str(end_c[1]), eased_progress)
                    current_final = (r1, r2)
                else:
                    current_final = r1
                
                widget.configure(**{prop: current_final})
                widget.after(delay, lambda: step(current_step + 1))
            except Exception as e:
                # Renk hatası olursa direkt sonuca git
                # print(f"Animasyon renk hatası: {e}")
                try: widget.configure(**{prop: end_color})
                except: pass
                return

        step(0)

    @staticmethod
    def shake_widget(widget, duration=300, magnitude=10):
        """
        Bir widget'ı sallar (Hatalı giriş için).
        Not: Widget 'place' geometry manager kullanıyorsa daha iyi çalışır.
        'pack' veya 'grid' için padding ile simüle edilir.
        """
        original_padx = 0
        try: original_padx = int(widget.pack_info().get('padx', 0)) if widget.winfo_manager() == 'pack' else 0
        except: pass
        
        steps = 10
        delay = duration // steps
        
        def step(current_step):
            try:
                if not widget.winfo_exists(): return
            except: return
            
            if current_step >= steps:
                # Sıfırla
                try:
                    if widget.winfo_manager() == 'pack':
                        widget.pack_configure(padx=original_padx)
                except: pass
                return
            
            # Sinüs dalgası ile sağa sola git
            offset = math.sin(current_step) * magnitude
            
            try:
                if widget.winfo_manager() == 'pack':
                    # Pack için padding ile oyna
                    widget.pack_configure(padx=(max(0, original_padx + offset), max(0, original_padx - offset)))
                elif widget.winfo_manager() == 'place':
                    # Place için x koordinatı ile oyna
                    current_x = int(widget.place_info().get('x', 0))
                    widget.place_configure(x=current_x + offset)
                
                widget.after(delay, lambda: step(current_step + 1))
            except: pass
            
        step(0)
