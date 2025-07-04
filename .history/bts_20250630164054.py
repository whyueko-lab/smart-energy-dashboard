import matplotlib.pyplot as plt

# Inisialisasi plot
fig, ax = plt.subplots(figsize=(8, 6))

# Garis utama drone (horizontal & vertikal)
drone_length = 6
ax.plot([-drone_length, drone_length], [0, 0], 'b', linewidth=3)  # horizontal
ax.plot([0, 0], [-drone_length, drone_length], 'b', linewidth=2)  # vertikal

# Fungsi untuk menggambar antena
def draw_antennas(base_x, base_y, spacing_y, is_left=True):
    for i in range(4):
        x_offset = -0.4 if is_left else 0.0
        x = base_x + x_offset
        y = base_y + (i - 1.5) * spacing_y
        ax.add_patch(plt.Rectangle((x, y), 0.4, 0.4, color='black'))

# Gambar 4 antena di sisi kiri batang horizontal
draw_antennas(base_x=-6.5, base_y=0, spacing_y=0.7, is_left=True)

# Gambar 4 antena di sisi kanan batang horizontal
draw_antennas(base_x=6.1, base_y=0, spacing_y=0.7, is_left=False)

# Styling plot
ax.set_xlim(-10, 10)
ax.set_ylim(-5, 5)
ax.set_aspect('equal')
ax.set_title('Top View Drone dengan 8 Antena (4 Kiri & 4 Kanan)')
ax.axis('off')  # Sembunyikan sumbu

plt.tight_layout()
plt.show()
