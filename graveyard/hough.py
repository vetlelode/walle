def houghTransform():
    linesP = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, None, 0, 0)
    cdstP = np.copy(cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR))
    print(xd)
    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]),
                     (0, 0, 255), 3, cv2.LINE_AA)
            print(l)


    cv2.imshow('', cdstP)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
