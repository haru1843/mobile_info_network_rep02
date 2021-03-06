---
puppeteer:
  header: "F20C004C 太田 剛史"
  displayHeaderFooter: true
  headerTemplate: '<div style="width:100%; border-bottom:0pt solid #eeeeee; margin: -12px 20px 0px 20px; font-size:6pt;"><p class="date" style="text-align:left"></p></div>'
  footerTemplate: '<div style="width:100%; text-align:right; border-bottom:0pt solid #eeeeee; margin: -18px 20px 0px 20px; font-size:6pt;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'
---

<div class='title-container'>
    <div class="title">移動情報ネットワーク特論</div>
    <div class="subtitle">レポート課題2</div>
    <div class="author">
    電気情報工学専攻 情報工学コース<br>
    F20C004C 太田剛史
    </div>
</div>

# 目次

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [目次](#目次)
- [移動がある場合のM/M/S/Sのシミュレーションの作成](#移動がある場合のmmssのシミュレーションの作成)
- [結果](#結果)
- [考察](#考察)
  - [1セルを通過するのにかかる時間における比較](#1セルを通過するのにかかる時間における比較)
  - [アーランB式との比較](#アーランb式との比較)

<!-- /code_chunk_output -->


# 移動がある場合のM/M/S/Sのシミュレーションの作成

以下に「移動が無い場合のM/M/S/Sのシミュレーション」を実行するためのスクリプトを示す.
今回利用した移動のモデルは, 1次元のセル構造を用いており, 中でも始点と終端をつなげた以下の図に示すような, 環状型のセル構造となっている.

@import "./img/loop_model.png" {width=500}

使用した言語は`Python 3.6.9`である.
プログラムの中身は`MobileTokenクラス`, `ServiceAreaManagerクラス`, `Simulatorクラス`の3つのクラスと, それらにパラメータを与え実行した`main関数`がある.
シミュレーションの結果はJSONファイルに出力されるようになっている.

また以下にシミュレーションのスクリプトを記すが, Github上にシミュレーションのスクリプトと描画のためのスクリプト, レポート作成に利用したmarkdownなどを載せてあるため, ネットワーク環境がある場合は下記のURLを参照していただきたい.
> https://github.com/haru1843/mobile_info_network_rep02

@import "./sim.py" {class="line-numbers"}

# 結果

上記のスクリプトを用いて, 横軸(対数軸)を呼量, 縦軸(線形軸)を呼損率としたグラフを作成した.
平均サービス提供時間を`1`として, それに対する「1セルを通過するのにかかる時間」に注目し, グラフを作成した(図中実線). また今回のモデルでは, セルの数を`5`つ, 各セル毎の容量を`3`つとしている. 
またグラフには容量が`15`の時のアーランB式の結果も載せている(図中破線).

@import "./img/block_rate.png" {width=800px}

<div style="page-break-before:always"></div>

# 考察

## 1セルを通過するのにかかる時間における比較

このような比較をした理由としては, 今回の移動のモデルに置いて, 端末の速度とセルの長さはそれぞれ別の関係でなく, 合わせて「1セルを通過するのにかかる時間」としてみたほうが効果的であると考えたためである. ここで言う1セルを通過するのにかかる時間$T_c$とはセルの長さ$l$と端末の速度$v$より, 以下のように表される.

$$
T_c = \frac{l}{v}
$$

結果のグラフを見ると, $T_c$が小さい値をとるほど呼損率が低くなる傾向が見られる. これは, $T_c$が小さくなるほど, 全体の呼に対して, ハンドオフ呼の割合が増加するためである(下記の図参照). 具体的には, 今回想定したモデルでは, 移動体の速度がすべて一定であるため, 何回もハンドオフしてもその分呼損が増えるわけではなく, ハンドオフの多くなればなるほど呼損の割合が減り, 呼損率が少なくなるため, ハンドオフ呼の割合が多くなればなるほど全体の呼損率も減少する.

@import "./img/handoff_rate.png" {width=800px}


ここからアーランB式を利用して, 上記シミュレーションを数式で出したいと思う.
移動が無い場合の呼損率は生起に成功した呼の数を$X_t$, 失敗した呼の数を$X_f$としたとき, $\frac{X_f}{X_t + X_f}$となる. 先に述べたことから, ハンドオフ呼に対してほとんど呼損が発生しないとすると, ハンドオフ呼の数を$Y$として, 移動を考慮した場合の呼損率は$\frac{X_f}{X_t + X_f + Y}$となる. このことから, 移動がない場合の呼損率から, 移動を考慮した呼損率を求めるには, $\frac{X_f}{X_t + X_f} \cdot Z = \frac{X_f}{X_t + X_f + Y}$となるような$Z$, つまり$Z=\frac{X_t + X_f}{X_t + X_f + Y}$を求めればよい. $X_t + X_f$はハンドオフ呼でない呼の総数であるため, 呼量としてみればよいため, $Y$を具体的に求めればよい. 
現状までで, 1セルあたりの通過時間$T_c$と呼量$a$から移動を考慮した呼損率を求める式を一旦まとめておくと以下のようになる.

$$
f(T_c, a) = E_S(a) \cdot \frac{a}{a + Y}
$$

ハンドオフ呼の数$Y$はサービス下にある平均トークン数$N_s$と各トークンがハンドオフするまでの平均時間$T_h$に大きく依存すると考えられる. $T_h$に関して, サービス提供時間が十分に長いと考えた時, ほとんどのハンドオフにかかる時間が$T_c$となるため, $T_h \approx T_c$と近似できる. またサービス下の平均トークン数はアーランB式による呼損率とサービス容量$S$より, 大まかに$E_S(a) \cdot S$と置くことができる. これらよりハンドオフ呼の数$Y$は以下のように示すことができる.

$$
Y \approx N_s \cdot \frac{1}{T_h} \approx \frac{E_S(a) \cdot S}{T_c}
$$

このことから, 推定式は以下のようになる.

$$
f(T_c, a) = E_S(a) \cdot \frac{a}{a + \frac{E_S(a) \cdot S}{T_c}}
$$

この推定式とシミュレーションによる値を比較したグラフを以下に示す.

@import "./img/calc_block_rate.png" {width=800px}


## アーランB式との比較

今回, グラフ中に比較のために載せたアーランB式のキャパシティは`15`としたが, これは大まかにみればシステム全体でキャパシティが15だとみなせるためである.
実際に, 1セルを通過するのにかかる時間$T_c$が長い場合とほとんど一致している様子が見られる.

しかしよく見ると, 呼量が少ない時にアーランB式の値よりも少し高い呼損率をとっていることがわかる.
これはアーランB式が1つのセルで考えているのに対し, 今回のモデルでは複数のセルで考えていることに起因すると思われる. つまり1つのセルが15のキャパシティを持っていれば確実に15までサービス対象を確保できるが, 複数のセルがあるモデルだと1つのセルにアクセスが集中すると全体で15確保する前に呼損が発生する. このため呼量が少ない段階だと, アーランB式の値よりも今回のモデルの方が呼損が大きくなったと考えられる.