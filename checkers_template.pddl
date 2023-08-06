MoveFL piece
pre: FFree(piece) LFree(piece) Own(piece)
preneg:
del: FFree(piece) LFree(piece)
add: RFree(piece) BFree(piece)

MoveFR piece
pre: FFree(piece) RFree(piece) Own(piece)
preneg:
del: FFree(piece) RFree(piece)
add: LFree(piece) BFree(piece)

MoveBL piece
pre: BFree(piece) LFree(piece) Kinged(piece) Own(piece)
preneg:
del: BFree(piece) LFree(piece)
add: RFree(piece) FFree(piece)

MoveBR piece
pre: BFree(piece) RFree(piece) Kinged(piece) Own(piece)
preneg:
del: BFree(piece) RFree(piece)
add: LFree(piece) FFree(piece)

King piece
pre: Own(piece)
preneg: FFree(piece)
del:
add: Kinged(piece)