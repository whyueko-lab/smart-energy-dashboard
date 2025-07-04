import matplotlib.pyplot as plt

# Inisialisasi plot
fig, ax = plt.subplots(figsize=(8, 8))

# Gambar garis sumbu drone (bentuk salib)
drone_length = 6
drone_width = 2

# Garis horizontal (sayap)
ax.plot([-drone_length, drone_length], [0, 0], 'b', linewidth=2)
# Garis vertikal (badan drone)
ax.plot([0, 0], [-drone_length, drone_length], 'b', linewidth=2)

# Fungsi untuk menggambar dua antena di setiap arah
def draw_antennas(x_base, y_base, dx, dy, label=None):
    spacing = 0.5
    for i in range(2):
        x = x_base + i * spacing * dx
        y = y_base + i * spacing * dy
        ax.add_patch(plt.Rectangle((x-0.2, y-0.2), 0.4, 0.4, color='black'))
        if label:
            ax.text(x, y + 0.3, label, fontsize=8, ha='center')

# Gambar antena di keempat sisi
draw_antennas(-drone_length, 0, 0, 1, label="A1")  # Kiri
draw_antennas(drone_length - 1.0, 0, 0, 1, label="A2")  # Kanan
draw_antennas(0, drone_length - 1.0, 1, 0, label="A3")  # Atas
draw_antennas(0, -drone_length, 1, 0, label="A4")  # Bawah

# Set skala dan gaya
ax.set_xlim(-8, 8)
ax.set_ylim(-8, 8)
ax.set_aspect('equal')
ax.set_title('Diagram Drone Top View dengan 8 Antena (2 per Arah)')
ax.axis('off')  # Hilangkan sumbu

plt.show()
