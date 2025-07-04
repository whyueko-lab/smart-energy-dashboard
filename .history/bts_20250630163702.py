import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Inisialisasi figure 3D
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Titik posisi drone
drone_pos = np.array([0, 0, 10])
ax.scatter(*drone_pos, color='blue', s=100, label='Drone')

# Posisi BTS di tanah (z = 0)
bts_positions = np.array([
    [-20, -20, 0],  # BTS 1
    [20, -20, 0],   # BTS 2
    [20, 20, 0],    # BTS 3
    [-20, 20, 0]    # BTS 4
])
ax.scatter(bts_positions[:,0], bts_positions[:,1], bts_positions[:,2], color='red', s=80, label='BTS')

# Gambar 8 antena mengarah ke 4 BTS (2 antena per BTS)
for i, bts in enumerate(bts_positions):
    for j in range(2):  # Dua antena per BTS
        offset = np.random.normal(scale=0.5, size=3)  # Sedikit variasi arah antena
        end_point = bts + offset
        ax.plot(
            [drone_pos[0], end_point[0]],
            [drone_pos[1], end_point[1]],
            [drone_pos[2], end_point[2]],
            color='green', linestyle='--'
        )

# Tambahkan label dan styling
ax.set_title('Diagram Drone dengan 8 Antena Mengarah ke 4 BTS')
ax.set_xlabel('X (meter)')
ax.set_ylabel('Y (meter)')
ax.set_zlabel('Z (meter)')
ax.legend()

# Batas sumbu
ax.set_xlim(-30, 30)
ax.set_ylim(-30, 30)
ax.set_zlim(0, 15)

plt.tight_layout()
plt.show()
