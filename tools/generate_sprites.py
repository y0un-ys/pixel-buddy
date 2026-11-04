"""Generate original, editable 4-frame pixel-art head sprite sheets (5 pets x 5 modes).
Requires Pillow only when regenerating artwork, not to run the bundled game.
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]/'assets'/'sprites'
ROOT.mkdir(parents=True,exist_ok=True)
ANIMALS={
 'dog':('#E2B58E','#F6DFC1','#B98264'),
 'cat':('#C8D2DF','#F4E3E6','#A5ADBE'),
 'bear':('#BE9476','#E8C4A5','#96735F'),
 'fox':('#EAA268','#FFE0BB','#BD7148'),
 'rabbit':('#F5E6EF','#FFF5F7','#E9ADBF'),
}
MODES=('typing','mouse','watching','gaming','idle')
INK='#483E53'

def frame(species,mode,step):
    fur,cream,shade=ANIMALS[species]
    im=Image.new('RGBA',(64,56),(0,0,0,0));d=ImageDraw.Draw(im)
    # Cozy oversized head, little ear movements, a subtle expressive wobble.
    dy=-1 if (step%2 and mode in ('typing','gaming')) else 0
    def r(box,c): d.rectangle((box[0],box[1]+dy,box[2],box[3]+dy),fill=c)
    def ell(box,c): d.ellipse((box[0],box[1]+dy,box[2],box[3]+dy),fill=c)
    if species=='dog':
        r((4,24,17,42),shade);r((47,24,60,42),shade)
        r((7,27,14,40),fur);r((50,27,57,40),fur)
    elif species=='cat':
        d.polygon([(6,29+dy),(11,5+dy),(27,20+dy)],fill=fur)
        d.polygon([(39,20+dy),(53,5+dy),(59,29+dy)],fill=fur)
        d.polygon([(12,22+dy),(14,12+dy),(22,21+dy)],fill='#F0ACB9')
        d.polygon([(43,21+dy),(52,12+dy),(54,22+dy)],fill='#F0ACB9')
    elif species=='bear':
        ell((8,10,28,29),shade);ell((39,10,58,29),shade)
        ell((13,15,23,25),cream);ell((44,15,53,25),cream)
    elif species=='fox':
        d.polygon([(3,28+dy),(15,3+dy),(29,23+dy)],fill=fur)
        d.polygon([(37,23+dy),(51,3+dy),(62,28+dy)],fill=fur)
        d.polygon([(12,23+dy),(16,13+dy),(23,23+dy)],fill=cream)
        d.polygon([(42,23+dy),(50,13+dy),(54,23+dy)],fill=cream)
    else:
        earshift=1 if step==3 else 0
        r((15,0+earshift,26,29),fur);r((40,0,51,29),fur)
        r((19,5+earshift,23,25),'#EAA6C5');r((44,5,48,25),'#EAA6C5')
    # Outline, face and muzzle. Crisp nearest-neighbor pixels at all scales.
    r((8,23,56,51),shade)
    r((6,30,58,47),shade)
    r((10,24,54,49),fur)
    r((8,32,56,45),fur)
    ell((21,38,45,52),cream)
    # Blinks & changes of gaze: independent animation states.
    blink=(step==3 and mode!='gaming') or (mode=='idle' and step in (1,2,3))
    shift=1 if mode=='mouse' and step%2 else 0
    if mode=='watching':
        r((15,33,29,41),'#EF7190');r((35,33,49,41),'#77C5E6')
        r((29,35,35,37),INK)
        r((17,35,19,36),'#FFE1E9');r((37,35,39,36),'#E5F9FF')
    elif blink:
        r((18,37,27,39),INK);r((39,37,48,39),INK)
    else:
        r((19+shift,34,27+shift,43),INK);r((39+shift,34,47+shift,43),INK)
        r((20+shift,35,22+shift,37),'#FFFFFF');r((40+shift,35,42+shift,37),'#FFFFFF')
    r((13,43,18,45),'#EB99A7');r((49,43,54,45),'#EB99A7')
    r((31,43,35,46),shade)
    if mode=='gaming' and step==2:
        r((31,48,36,49),INK);r((32,50,35,51),'#DA8F9C')
    elif mode=='idle':
        r((30,48,37,48),INK)
    else:
        r((30,48,37,49),INK);r((32,50,35,50),'#D78F9F')
    if species=='cat':
        for yy in (44,47):
            r((9,yy,17,yy),'#EAD6D8');r((47,yy,55,yy),'#EAD6D8')
    if species=='fox':
        r((11,45,18,47),cream);r((46,45,53,47),cream)
    return im


def generate():
    for species in ANIMALS:
        for mode in MODES:
            sheet=Image.new('RGBA',(64*4,56),(0,0,0,0))
            for step in range(4):sheet.paste(frame(species,mode,step),(step*64,0))
            sheet.save(ROOT/f'{species}_{mode}.png',optimize=True)
    print('Generated 25 sprite sheets:',ROOT)
if __name__=='__main__':generate()
