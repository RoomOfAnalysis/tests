import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

# https://stackoverflow.com/questions/35740374/orthogonal-projection-of-point-onto-line
# https://stackoverflow.com/questions/51905268/how-to-find-closest-point-on-line
def project2d(points, p1, p2, threshold = 0.05, point_in_between = False):
    abs = np.linalg.norm(p2 - p1)
    dir = (p2-p1) / abs
    norm = np.array([(p1[1] - p2[1])/abs, (p1[0] - p2[0])/abs])
    plane_normal = np.array([norm[0], norm[1], 0])
    plane_center = np.array([p1[0], p1[1], 0])
    #print(abs, dir, norm, plane_normal, plane_center)
    plane_pts = []
    for pt in points:
        if np.abs((pt - plane_center).dot(plane_normal)) <= threshold:
            plane_pts.append(pt)
    if len(plane_pts) == 0: return np.array([]);        
    plane_pts = np.array(plane_pts)
    #print(plane_pts)
    res = []
    if point_in_between:
        x1 = p1[0] * dir[0] + p1[1] * dir[1]
        x2 = p2[0] * dir[0] + p2[1] * dir[1]
        lhs = x1 if x1 < x2 else x2
        rhs = x2 if x1 < x2 else x1
        for pt in plane_pts:
            x = pt[0] * dir[0] + pt[1] * dir[1]
            # points outside <p1, p2>
            if x < lhs or x > rhs:
                continue
            res.append(np.array([x, pt[2]]))
    else:
        for pt in plane_pts:
            res.append(np.array([pt[0] * dir[0] + pt[1] * dir[1], pt[2]]))
    res = np.array(res) 
    #print(res.shape)  
    np.unique(res[np.argsort(res[:, 0])], axis=0)
    return res        


def extant_file(x):
    """
    'Type' for argparse - checks that file exists but does not open.
    """
    if not os.path.exists(x):
        # Argparse uses the ArgumentTypeError to give a rejection message like:
        # error: argument input: x does not exist
        raise argparse.ArgumentTypeError("{0} does not exist".format(x))
    return x

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot cross section profiles of input mesh.')
    parser.add_argument('-f' '--file', dest="filepath", required=True, nargs=1, 
                        type=extant_file,
                        #type=argparse.FileType('r'),
                        help='mesh file path for plotting')

    args = parser.parse_args()
    pcd = o3d.io.read_triangle_mesh(os.path.abspath(args.filepath[0]))
    aabb = pcd.get_axis_aligned_bounding_box()
    aabb.color = (1, 0, 0)
    print(aabb)
    #obb = pcd.get_oriented_bounding_box()
    #obb.color = (0, 1, 0)
    #print(obb)
    #o3d.visualization.draw_geometries([pcd, aabb, obb])
    points = np.asarray(pcd.vertices)

    pts2d_x = project2d(points, np.array([-1, aabb.get_center()[1]]), np.array([1, aabb.get_center()[1]]), 0.05)
    pts2d_y = project2d(points, np.array([aabb.get_center()[0], -1]), np.array([aabb.get_center()[0], 1]), 0.05)
    pts2d_xy = project2d(points, np.array([aabb.get_min_bound()[0], aabb.get_min_bound()[1] + aabb.get_extent()[1] / 3]), np.array([aabb.get_center()[0], aabb.get_center()[1]]), 0.05)
    #pts2d_xy = project2d(points, np.array([aabb.get_min_bound()[0], aabb.get_min_bound()[1]]), np.array([aabb.get_center()[0], aabb.get_center()[1]]), 0.1)

    fig, ax = plt.subplots(3, sharex=True)
    fig.suptitle('cross section plots')
    ax[0].scatter(pts2d_x[:, 0], pts2d_x[:, 1], marker='o')
    ax[0].set_title('Axis X')
    ax[1].scatter(pts2d_y[:, 0], pts2d_y[:, 1], marker='o')
    ax[1].set_title('Axis Y')
    ax[2].scatter(pts2d_xy[:, 0], pts2d_xy[:, 1], marker='o')
    ax[2].set_title('XY')

    for a in ax.flat:
        a.set(xlabel='x', ylabel='y')
    for a in ax.flat:
        a.label_outer()

    plt.show()

