"""Write tbl/jp.tbl (glyph code -> char) from tbl/jp_auto.tsv (tools/ocr_font.py) plus the hand fixes below.

Codes are the 16-bit values as stored in text (big-endian pair hi,lo; e.g. 8140 = glyph 0 = space).
python -X utf8 tools/mktbl.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font as F

ROOT = Path(__file__).resolve().parents[1]

# glyphs 0..287, read off the font sheet (SJIS order subset)
HEAD = ('　、。・：？！々ー／～（）《》「」『』【】＋－×∞￥＄％＆＊＠○●◎◇◆□■△▽▼→←↑↓⇒∀≪≫♪'
        '０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
        'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ')
HIRA = ''.join(chr(c) for c in range(0x3041, 0x3094) if chr(c) not in 'ゎゐゑ')
KATA = ''.join(chr(c) for c in range(0x30A1, 0x30F4) if chr(c) not in 'ヮヰヱ') + 'ヴ'
TAIL = 'ΓΔΘΛΞΠΣΦΨΩ' + '〒♥◀▶Ⅱ'   # 283 is a one-off glyph (looks like a t-crossed "れ"); shown as 〒 placeholder

# glyph index -> char, fixes to the OCR alignment (checked against tools/tblreview.py sheets)
FIX = {
    291: '圧', 292: '鮎', 359: '科', 316: '陰', 335: '援', 349: '屋', 355: '何', 361: '架', 374: '回', 382: '絵', 386: '街',
    399: '寒', 402: '寛', 403: '感', 406: '管', 407: '鑑', 415: '顔', 416: '願', 420: '基', 423: '機', 429: '起',
    436: '議', 443: '宮', 451: '級', 455: '許', 470: '玉', 483: '係', 491: '継', 516: '元', 530: '湖', 533: '語',
    534: '護', 539: '効', 545: '工', 546: '幸', 555: '皇', 556: '紅', 559: '荒', 564: '香', 565: '高', 572: '骨',
    576: '困', 589: '祭', 591: '在', 596: '作', 597: '削', 598: '索', 600: '皿', 603: '山', 605: '産', 606: '算',
    610: '使', 611: '司', 657: '若', 658: '弱', 642: '耳', 643: '自', 656: '借', 659: '主', 678: '住', 683: '宿', 684: '出', 698: '除', 715: '笑',
    1177: '連', 797: '祖', 814: '増', 740: '神', 744: '震', 787: '占', 798: '素', 799: '組', 803: '想', 808: '相', 815: '蔵', 830: '太', 839: '退',
    849: '達', 850: '辰', 863: '値', 874: '柱', 916: '渡', 937: '闘', 938: '働', 941: '導', 984: '白', 985: '薄',
    986: '漠', 989: '畑', 991: '抜', 994: '反', 995: '板', 996: '版', 998: '飯', 1015: '氷', 1019: '敏', 1023: '富',
    1024: '怖', 1038: '分', 1040: '文', 1048: '変', 1050: '返', 1056: '墓', 1066: '訪', 1068: '坊', 1078: '牧',
    1081: '妹', 1082: '枚', 1084: '万', 1085: '味', 1086: '未', 1087: '密', 1122: '有', 1133: '様', 1136: '葉',
    1137: '要', 1139: '欲', 1165: '林', 1166: '輪', 1179: '労', 1183: '和',
}
# 1186.. appended out of JIS order
APPENDED = '櫻澤濱円乙喚奇狂賢魂疾狩祝盾召晶杖陣跡賊脱笛兎徒盗縛符臨伊稲浦岳吉享佐寿秀父亮鹿嶋朋柳隆'


def build():
    auto = {}
    for line in open(ROOT / 'tbl/jp_auto.tsv', encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        auto[int(p[0])] = p[2]
    head = HEAD + HIRA + KATA + TAIL
    assert len(HEAD) == 112 and len(HIRA) == 80 and len(KATA) == 81 and len(head) == 288, (len(HEAD), len(HIRA), len(KATA), len(head))
    t = {}
    for i in range(1240):
        if i < 288:
            t[i] = head[i]
        elif i >= 1186:
            k = i - 1186
            if k < len(APPENDED):
                t[i] = APPENDED[k]
        else:
            t[i] = FIX.get(i, auto.get(i, ''))
    return t


def main():
    t = build()
    vals = [v for v in t.values() if v]
    assert len(vals) == len(set(vals)), 'duplicate chars in table'
    with open(ROOT / 'tbl/jp.tbl', 'w', encoding='utf-8', newline='\n') as f:
        for i in sorted(t):
            if t[i]:
                f.write('%04X=%s\n' % (F.index_to_code(i), t[i]))
    print(len(t), 'entries -> tbl/jp.tbl')


if __name__ == '__main__':
    main()
