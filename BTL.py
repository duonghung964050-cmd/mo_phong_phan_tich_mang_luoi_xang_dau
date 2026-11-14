import random
import matplotlib.pyplot as plt
import networkx as nx
from collections import deque

print("======================================================================")
print("     CHƯƠNG TRÌNH MÔ PHỎNG & PHÂN TÍCH MẠNG LƯỚI PHÂN PHỐI XĂNG DẦU     ")
print("======================================================================")

try:
    num_warehouses = int(input(">> Nhập số lượng kho chính (Đề nghị >= 3): "))
    num_gas_stations = int(input(">> Nhập tổng số lượng trạm xăng (Đề nghị >= 17 để tổng đỉnh >= 20): "))
except ValueError:
    print("[Cảnh báo] Giá trị nhập không hợp lệ! Hệ thống sẽ tự động dùng mặc định: 3 kho, 17 trạm.")
    num_warehouses = 3
    num_gas_stations = 17

# Random số lượng trạm bị cô lập (2 hoặc 3 trạm)
num_isolated = random.choice([2, 3])
print(f"\n[Thông tin] Số lượng trạm xăng bị cô lập được random ngẫu nhiên là: {num_isolated} trạm.")

if num_gas_stations < num_isolated + 5:
    num_gas_stations = num_isolated + 6
    print(f"[Điều chỉnh] Đã tự động cập nhật số lượng trạm xăng lên {num_gas_stations} để đảm bảo cấu trúc đồ thị.")

warehouses = [f"Kho_Chinh_{i}" for i in range(1, num_warehouses + 1)]
gas_stations = [f"Tram_G{i}" for i in range(1, num_gas_stations + 1)]

G = nx.Graph()
G.add_nodes_from(warehouses, type="Warehouse")
G.add_nodes_from(gas_stations, type="GasStation")


print("\n----------------------------------------------------------------------")
print("BƯỚC 1: XÂY DỰNG ĐỒ THỊ MẠNG LƯỚI PHÂN PHỐI & ĐÁNH DẤU TẬP ĐỈNH KHO CHÍNH")
print("----------------------------------------------------------------------")

S = set(warehouses)
print(f"-> Tập hợp S các đỉnh kho chính được đánh dấu riêng biệt: {S}")

edge_pairs = []

# Kết nối liên thông các kho chính
for i in range(len(warehouses) - 1):
    edge_pairs.append((warehouses[i], warehouses[i + 1]))

isolated_group = gas_stations[-num_isolated:]
connected_stations = gas_stations[:-num_isolated]

# Kết nối các trạm thông thường về kho chính
for i, station in enumerate(connected_stations):
    target_wh = warehouses[i % len(warehouses)]
    edge_pairs.append((station, target_wh))
    if i > 0:
        edge_pairs.append((station, connected_stations[i - 1]))

# THÊM CÁC CẠNH NỘI BỘ CỦA TRẠM CÔ LẬP VÀO NGAY TỪ ĐẦU ĐỂ ĐẢM BẢO KHÉP KÍN
if num_isolated == 2:
    edge_pairs.append((isolated_group[0], isolated_group[1]))
elif num_isolated == 3:
    # Nối đủ 3 cạnh để tạo thành hình TAM GIÁC khép kín hoàn chỉnh giữa 3 trạm cô lập
    edge_pairs.append((isolated_group[0], isolated_group[1]))
    edge_pairs.append((isolated_group[1], isolated_group[2]))
    edge_pairs.append((isolated_group[0], isolated_group[2]))

# Bổ sung các cạnh ngẫu nhiên giữa các trạm thông thường cho đủ tối thiểu 26 cạnh
while len(edge_pairs) < 26:
    u = random.choice(connected_stations)
    v = random.choice(connected_stations)
    if u != v and (u, v) not in edge_pairs and (v, u) not in edge_pairs:
        edge_pairs.append((u, v))

# Thêm cạnh và gán trọng số vào đồ thị G
edges_with_weights = []
for u, v in edge_pairs:
    weight_val = random.randint(1, 10)
    edges_with_weights.append((u, v, {"weight": weight_val}))

G.add_edges_from(edges_with_weights)

# Tạo đồ thị thực địa G_full (sinh thêm các tuyến đường chưa cấp phép xuất phát từ trạm cô lập)
G_full = G.copy()
unpermitted_edges = []
all_nodes_list = list(G.nodes())

for iso in isolated_group:
    targets = random.sample(all_nodes_list, k=min(6, len(all_nodes_list)))
    for target in targets:
        if target != iso and not G_full.has_edge(iso, target) and not G_full.has_edge(target, iso):
            w_val = random.randint(2, 9)
            unpermitted_edges.append((iso, target, {"weight": w_val}))

for _ in range(10):
    u = random.choice(gas_stations)
    v = random.choice(gas_stations)
    if u != v and not G_full.has_edge(u, v) and not G_full.has_edge(v, u):
        w_val = random.randint(3, 10)
        unpermitted_edges.append((u, v, {"weight": w_val}))

G_full.add_edges_from(unpermitted_edges)

print(f"-> Tổng số đỉnh trong đồ thị: {G.number_of_nodes()} (Đạt yêu cầu tối thiểu >= 20 đỉnh)")
print(f"-> Tổng số cạnh có phép lưu thông: {G.number_of_edges()} (Đạt yêu cầu tối thiểu >= 26 cạnh)")
print(f"-> Tổng số cạnh trên thực địa (kể cả chưa cấp phép): {G_full.number_of_edges()}")


print("\n----------------------------------------------------------------------")
print("BƯỚC 2: DUYỆT BFS ĐA NGUỒN (MULTI-SOURCE) XUẤT PHÁT TỪ MỌI KHO CHÍNH")
print("----------------------------------------------------------------------")

def multi_source_bfs(graph, sources):
    visited = set(sources)
    queue = deque(sources)
    
    while queue:
        current = queue.popleft()
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                
    return visited

reachable_nodes = multi_source_bfs(G, S)
print(f"-> Hoàn thành duyệt Multi-source BFS.")
print(f"-> Tổng số đỉnh có thể đến được từ ít nhất một kho chính trong S: {len(reachable_nodes)}")


print("\n----------------------------------------------------------------------")
print("BƯỚC 3: XÁC ĐỊNH CÁC TRẠM XĂNG BỊ MẤT KẾT NỐI NGUỒN CUNG")
print("----------------------------------------------------------------------")

all_gas_stations_set = set(gas_stations)
isolated_stations = all_gas_stations_set - reachable_nodes

print(f"-> Danh sách toàn bộ các trạm xăng: {sorted(list(all_gas_stations_set))}")
print(f"-> Danh sách các trạm xăng BỊ CÔ LẬP (không có đường đi từ bất kỳ kho chính nào):")
for idx, st in enumerate(sorted(list(isolated_stations)), 1):
    print(f"   {idx}. Trạm: {st}")


print("\n----------------------------------------------------------------------")
print("BƯỚC 4: TÌM ĐƯỜNG NGẮN NHẤT TỪ TRẠM BỊ CÔ LẬP ĐẾN TRỰC TIẾP CÁC KHO CHÍNH (S)")
print("----------------------------------------------------------------------")

recommendations = {}
proposed_edges_set = set()

for station in sorted(list(isolated_stations)):
    min_dist = float('inf')
    best_path = None
    best_target_wh = None

    for wh in S:
        try:
            length = nx.dijkstra_path_length(G_full, source=station, target=wh, weight='weight')
            if length < min_dist:
                min_dist = length
                best_path = nx.dijkstra_path(G_full, source=station, target=wh, weight='weight')
                best_target_wh = wh
        except nx.NetworkXNoPath:
            continue

    recommendations[station] = {
        "path": best_path,
        "distance": min_dist,
        "target": best_target_wh
    }

    if best_path:
        for i in range(len(best_path) - 1):
            u_node, v_node = best_path[i], best_path[i+1]
            if not G.has_edge(u_node, v_node):
                edge_tuple = tuple(sorted((u_node, v_node)))
                proposed_edges_set.add(edge_tuple)

    print(f"- Trạm bị cô lập [{station}]:")
    print(f"  + Kho chính kết nối ngắn nhất: {best_target_wh}")
    print(f"  + Tuyến đường đề xuất xin cấp phép tối ưu về kho: {' -> '.join(best_path if best_path else [])}")
    print(f"  + Tổng khoảng cách/chi phí ngắn nhất: {min_dist} km")


# ==============================================================================
# XUẤT BẢNG TỔNG HỢP CÁC TUYẾN ĐƯỜNG CHƯA CẤP PHÉP RA TERMINAL
# ==============================================================================
all_unpermitted_edges = []
for u, v, data in G_full.edges(data=True):
    if not G.has_edge(u, v) and not G.has_edge(v, u):
        all_unpermitted_edges.append((u, v, data.get('weight', 1)))

print("\n----------------------------------------------------------------------")
print("[Terminal] BẢNG TỔNG HỢP TẤT CẢ CÁC TUYẾN ĐƯỜNG CHƯA CẤP PHÉP:")
print("=" * 65)
print(f"{'STT':<5} | {'Tuyến đường (A - B)':<30} | {'Trọng số (km)':<15}")
print("-" * 65)
for idx, (u, v, w) in enumerate(all_unpermitted_edges, 1):
    print(f"{idx:<5} | {f'{u} - {v}':<30} | {f'{w} km':<15}")
print("=" * 65)


# ==============================================================================
# PHẦN 5: XUẤT BÁO CÁO TỔNG HỢP VÀ TRỰC QUAN HÓA SƠ ĐỒ MẠNG LƯỚI (BƯỚC 5)
# ==============================================================================
print("\n----------------------------------------------------------------------")
print("BƯỚC 5: XUẤT BÁO CÁO TỔNG HỢP VÀ TRỰC QUAN HÓA SƠ ĐỒ MẠNG LƯỚI")
print("----------------------------------------------------------------------")
print("Đang khởi tạo biểu đồ trực quan hóa đồ thị mạng lưới phân phối...")

plt.figure(figsize=(18, 12))
pos = nx.spring_layout(G_full, seed=42, k=0.35, iterations=250)

# Cố định vị trí nhóm trạm cô lập sang phía bên trái:
# Nếu có 3 trạm, xếp thành hình tam giác nhỏ gọn để các cạnh nối không bị đè lên nhau
if num_isolated == 3:
    pos[isolated_group[0]] = (-1.8, 0.4)
    pos[isolated_group[1]] = (-1.2, 0.4)
    pos[isolated_group[2]] = (-1.5, -0.3)
elif num_isolated == 2:
    pos[isolated_group[0]] = (-1.5, 0.3)
    pos[isolated_group[1]] = (-1.5, -0.3)

node_colors_list = []
for node_item in G_full.nodes():
    if node_item in S:
        node_colors_list.append('orange')
    elif node_item in isolated_stations:
        node_colors_list.append('red')
    else:
        node_colors_list.append('skyblue')

nx.draw_networkx_nodes(G_full, pos, node_color=node_colors_list, node_size=850, alpha=0.95)

# Vẽ các cạnh được phép lưu thông (nét liền màu xám) - bao gồm cả tam giác nội bộ nhóm cô lập
nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.5, edge_color='gray')

edge_labels_permitted = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels_permitted, font_size=8, font_color='darkgreen')

# Vẽ các tuyến chưa cấp phép (nét chấm màu xám nhạt)
unpermitted_list_for_draw = [(u, v) for u, v, w in all_unpermitted_edges]
nx.draw_networkx_edges(G_full, pos, edgelist=unpermitted_list_for_draw, width=1.0, alpha=0.4, edge_color='gray', style='dotted')

unpermitted_labels = { (u, v): w for u, v, w in all_unpermitted_edges }
nx.draw_networkx_edge_labels(G_full, pos, edge_labels=unpermitted_labels, font_size=7, font_color='gray')

# Vẽ đường đề xuất tối ưu (nét đứt màu xanh lá đậm)
if proposed_edges_set:
    proposed_edges_list = list(proposed_edges_set)
    nx.draw_networkx_edges(G_full, pos, edgelist=proposed_edges_list, width=2.5, edge_color='forestgreen', style='dashed')
    
    proposed_edge_labels = { (u, v): G_full[u][v]['weight'] for u, v in proposed_edges_list }
    nx.draw_networkx_edge_labels(G_full, pos, edge_labels=proposed_edge_labels, font_size=8, font_color='red')

nx.draw_networkx_labels(G_full, pos, font_size=10, font_weight='bold', font_family='sans-serif')

plt.title(
    f"SƠ ĐỒ MẠNG LƯỚI PHÂN PHỐI XĂNG DẦU\n"
    f"(Tổng số đỉnh: {G_full.number_of_nodes()} | Số cạnh được cấp phép: {G.number_of_edges()} | Trạm cô lập: {num_isolated})",
    fontsize=14,
    fontweight='bold',
    color='navy'
)
plt.axis('off')
plt.tight_layout()

print("-> Hoàn tất! Đang hiển thị cửa sổ đồ thị trực quan...")
plt.show()