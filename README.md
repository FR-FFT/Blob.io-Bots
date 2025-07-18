## Videos
(In all of the videos, I am playing as neuro and the other neuro is a bot controlled by me.)


https://github.com/user-attachments/assets/b19f60c8-841e-4f05-ba1f-dc814a3d61cc



https://github.com/user-attachments/assets/77d22d3b-885d-41da-94a2-7ff1cdba61dd




https://github.com/user-attachments/assets/bd0f4ee4-aef1-44c9-877b-ed95ab0582f8


## To run
* Download all of the files. The first thing to do is to obtain the JWTs needed for authentication. There are two ways to do this:
### Manually
* Open an incognito browser window. Go to blobgame.io, open the developer tools (ctrl + shift + i), and switch to the network tab.
<img width="570" height="37" alt="image" src="https://github.com/user-attachments/assets/055b5136-016c-441e-bfe0-46fd61d593e4" />

* Change the filter to socket.
<img width="587" height="28" alt="image" src="https://github.com/user-attachments/assets/6ee7e773-e3ab-4654-81fd-9e2769fde73f" />

* Enter a game. Ignore any warnings about it being insecure - this is because blob.io uses http instead of https.
There will be a websocket connection in the dev tools.
<img width="670" height="177" alt="image" src="https://github.com/user-attachments/assets/6a465d32-e6c9-4c14-a199-3c9b5f95689a" />

* Copy all of the long text in Sec-Websocket-Protocol after 7, 3, WaWdft, (you can test on jwt.io whether you have done it correctly - it should be a valid jwt).
<img width="667" height="690" alt="image" src="https://github.com/user-attachments/assets/9c46ccfe-6f6a-47ac-a6c9-4a13be570c48" />

* Paste this into jwts.txt, removing what was there before (because they won't work for more than a few days).
* You will probably want at least two of these, so repeat the process.

### Semi-automatically
* *Install [captcha-harvester](https://github.com/NoahCardoza/CaptchaHarvester). It will not run on the latest python versions, so use either `python3.9 -m pip install captcha-harvester`, or `uv python pin 3.9` and `uvx harvester --from captcha-harvester`
* *Run `harvester -k 6LefTNUUAAAAAKgrowGdOhrnKxcm2ql40YRck04V -d custom.client.blobgame.io recaptcha-v2` and run get_jwts.py at the same time (the captcha tokens seem to be time-limited, they will invalidate if not used withina few minutes).

## Running the bots
* First run server.py. Modify `TARGET_SERVER_IP_PORT = "51.195.60.134:6001"` to change the server. Modify `"name": f"neuro",` to change the bot names.
* Install script.js using a userscript extension like tampermonkey, violetmonkey, etc.
* Make sure you connect to the same server.
* Use 'a' to split the bots and 's' to feed, and 'o' to toggle the bots going to your mouse.

# How I Reverse Engineered this

First of all, https://github.com/Lemons1337/Blob.io-Bots was helpful (though significantly outdated). 
We can also see from the packets that Blob.io is using MultiOgar:
<img width="870" height="153" alt="image" src="https://github.com/user-attachments/assets/d947a6ca-9baa-46c0-b16d-5175f090df44" />

Though it has been modified significantly.
By replicating the initial three messages (which seem to just connect to the server) and then the latter 2 (which set the name and then spawn the player), it is straightforward to connect to the server, though it will disconnect if any of the headers are different, or if the JWT which is provided through Sec-Accept-Protocol is invalid. For testing purposes, the simplest thing to do is copy the JWT from an existing connection. 
This works, but the server will kill the connection after a few seconds. Looking through the packets sent, most of them start with opcode 10, signifying node updates. However, there is a group of packets that stand out:
<img width="844" height="142" alt="image" src="https://github.com/user-attachments/assets/ca4dd3ca-87b5-47ae-a6f8-f1bb789887ae" />

This some kind of secondary authentication, to ensure the client is valid. We can verify this by modifying the packet, which I did with mitm proxy, and which causes even the browser to fail. Therefore it is necessary to look at the code executed on the client. 
The main code can be found in sources as html-0.js. The filesystem is exposed at http://custom.client.blobgame.io/html/, and the actual code is loaded from http://custom.client.blobgame.io/html/B3C8E257EB66FC949F9081983031C066.cache.js (though it mary vary depending on user agent).
Looking through the code, this part of the code is particularly interesting:
```js
function wxe(b, c) {
    var d, e, f, g, h, i, j, k, l, m, n, o, p, q;
    if (b.q) {
        return
    }
    d = jGe(new tIe(c), (yGe(),
    wGe));
    (Yse(),
    Qse) || Ate(b.j, d);
    e = 0;
    switch (d.CX(e++) & 255) {
    case 16:
        try {
            b.H ? Aye(d, e, b) : tye(d, e, b);
            Hxe(b);
            yxe(b)
        } catch (a) {
            a = Yke(a);
            if (q1d(a, 34)) {
                k = a;
                l1b(k, (_Fe(),
                ZFe), '', '')
            } else
                throw Zke(a)
        }
        break;
    case 17:
        Bye(b.J, d.vU(e), d.vU(e + 4));
        Cye(b.J, d.vU(e + 8));
        break;
    case 21:
        (_Fe(),
        $Fe).QW('21');
    case 20:
        (_Fe(),
        $Fe).QW('20');
        break;
    case 32:
        h3b(b.B, d.yU(e));
        b.o = false;
        break;
    case 49:
        if (Use) {
            nye(b.s, d, b.B, b.F);
            Cf(b.u, b.s)
        }
        break;
    case 50:
        oye(b.s, d);
        Cf(b.u, b.s);
        break;
    case 53:
        qye(d, b.b);
        break;
    case 65:
        q = d.yU(e);
        Sxe(b.K, ZDe(q));
        break;
    case 67:
        rre(b.v, d);
        for (g = new LKe(b.d); g.a < g.c.a.length; ) {
            f = KKe(g);
            dye(f, l3b(b.n, f.J) && !Zse)
        }
        break;
    case 64:
        QAe(b.t, cBe(d.DX(e)));
        RAe(b.t, cBe(d.DX(e + 8)));
        OAe(b.t, cBe(d.DX(e + 16)));
        PAe(b.t, cBe(d.DX(e + 24)));
        use(b.C);
        break;
    case 80:
        zye(d);
        break;
    case 99:
        Tse && !nxe && Bf(b.u, oxe(d, e));
        break;
    case 101:
        try {
            b.F = d.yU(e);
            if (b.F >= 3) {
                e += 4;
                l = d.yU(e);
                (l & 1) != 0 && (b.s.a = true,
                undefined);
                (l & 2) != 0 && (Zse = true);
                pxe.H = (l & 16) != 0;
                pxe.H && (_Fe(),
                $Fe).QW('Using shortPackets');
                pxe.G = (l & 64) != 0;
                pxe.G && (_Fe(),
                $Fe).QW('Using shortNamesPackets')
            }
        } catch (a) {
            a = Yke(a);
            if (q1d(a, 34)) {
                b.F = 1
            } else
                throw Zke(a)
        }
        break;
    case 123:
        h = d.BU(e);
        i = d.BU(e += 2);
        m = d.BU(e += 2);
        n = d.BU(e += 2);
        j = d.BU(e += 2);
        o = d.BU(e + 2);
        p = b.C.u;
        j != o && (p.b = true);
        w3(p.a, h, i);
        U2(u3(x3(p.f, p.a), 1 / p.e), 0.5, 0.5);
        w3(p.c, m, n);
        U2(u3(x3(p.i, p.c), 1 / p.e), 0.5, 0.5);
        p.g = j / p.e;
        p.j = o / p.e;
        break;
    case 253:
        jye(d, b.I);
    }
}
```
In this case the opcode in hex matches with the decimal 253.
```js
function jye(a, b) {
    var c, d, e, f;
    e = a.yU(1);
    f = a.yU(5);
    d = e & f | e << f ^ e;
    c = lGe(5);
    jGe(c, (yGe(),
    wGe));
    jIe(c, -3);
    mIe(c, d);
    uVd(b.e) == 1 && nBe(b, c.a)
}```
The lines `e = a.yU(1);` and `f = a.yU(5);` read two 32-bit little-endian integers from the binary buffer (skipping the opcode). It then performs some bitshifting to produce a new number, d, which is then written back into a new buffer and sent in response.

If we add this to the code, the bots connect normally. Controlling them is simple enough - they send mouse packets as the x and y coordinates of the mouse, and the server doesn't seem to verify that these coordinates are within their viewbox.

This works, but to respawn the bots when they die, we need to know when they die. Periodically sending respawn requests (even when alive) will cause the server to ban you, probably as an anti-bot mechanism, since this is what https://github.com/Lemons1337/Blob.io-Bots does. In hindsight, checking for the CameraUpdate packet probably would have sufficed, but for this, I decided to copy the client's logic.
Following the code from earlier:
```js
    case 16:
        try {
            b.H ? Aye(d, e, b) : tye(d, e, b);
            Hxe(b);
            yxe(b)
        } catch (a) {
            a = Yke(a);
            if (q1d(a, 34)) {
                k = a;
                l1b(k, (_Fe(),
                ZFe), '', '')
            } else
                throw Zke(a)
        }
        break;
```
```function Aye(b, c, d) {
    var e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, A, B, C, D, F, G, H, I, J, K, L, M;
    d.r = (_Fe(),
    ele(aSe()));
    d.i = false;
    g = 0;
    m = b.BU(c) & USe;
    c += 2;
    for (j = 0; j < m; ++j) {
        n = E2b(d.e, b.BU(c) & USe);
        H = E2b(d.e, b.BU(c + 2) & USe);
        c += 4;
        if (!!H && !!n && dte) {
            H.g = d.r;
            aye(H, n)
        }
    }
    c == 1 && (c += 2);
    for (; ; ) {
        g = b.BU(c) & USe;
        c += 2;
        if (g == 0) {
            break
        }
        e = E2b(d.e, g);
        I = b.BU(c);
        c += 2;
        J = b.BU(c);
        c += 2;
        D = b.BU(c) & USe;
        c += 2;
        p = b.CX(c++);
        v = (p & 1) != 0;
        t = (p & 2) != 0;
        u = false;
        d.F == 8 && (u = (p & 64) != 0);
        f = null;
        i = 0;
        if (t) {
            i = b.BU(c);
            c += 2;
            (!e || e.e != i) && (f = (yre(),
            K = wre[(i & USe & 63488) >> 11],
            L = xre[(i & USe & 2016) >> 5],
            M = wre[i & USe & 31],
            new Ri(K / 255,L / 255,M / 255,1)))
        }
        SFe(d.D, d.D.a.length);
        C = null;
        if ((p & 4) != 0) {
            if (d.G) {
                F = b.BU(c) & USe;
                c += 2;
                w = E2b((Qte(),
                Nte), F);
                !!w && (C = w.e)
            } else {
                c += 1;
                for (; ; ) {
                    G = b.CX(c++);
                    if (G == 0)
                        break;
                    if (Mye(d.f, (Hze(),
                    Eze))) {
                        try {
                            (E2b(d.e, g) == null || E2b(d.e, g).B == null) && LFe(d.D, G & USe)
                        } catch (a) {
                            a = Yke(a);
                            if (q1d(a, 34)) {
                                l = a;
                                l1b(l, ZFe, '', '')
                            } else
                                throw Zke(a)
                        }
                    }
                }
                if (Mye(d.f, (Hze(),
                Eze))) {
                    C = d.D.a.toLowerCase();
                    SFe(d.D, d.D.a.length)
                }
            }
        }
        while ((b.BU(c) & USe) != 0) {
            LFe(d.D, b.BU(c) & USe);
            c += 2
        }
        A = d.D.a.length == 0 ? null : d.D.a;
        c += 2;
        r = (p & 8) != 0;
        B = 0;
        if (r) {
            B = b.BU(c) & USe;
            c += 2;
            A != null ? J2b(d.w, B, A) : (A = E2b(d.w, B))
        }
        q = (p & 128) != 0;
        h = -1;
        if (q) {
            h = b.CX(c);
            if (d.F >= 9) {
                u = (h & 128) != 0;
                h = h & 127
            }
            ++c
        }
        if (e) {
            fye(e);
            e.F = e.M;
            e.G = e.O;
            e.H = e.R;
            e.I = e.S;
            e.C = I;
            e.D = J;
            e.w = D;
            e.A = D;
            if (i != 0) {
                e.e = i;
                bye(e, f)
            }
            e.s != v && (e.s = v,
            e.t = v && e.d == (Wze(),
            Qze).a)
        } else {
            e = new gye(g,B,I,J,D,f,v,A,C,h);
            e.i = p;
            e.r = (p & 16) != 0;
            e.u = (p & 32) != 0;
            e.p = u;
            e.e = i
        }
        e.Q = d.r;
        if (d.F > 7 && u && !$re(d.A, e)) {
            Zre(d.A, e);
            h3b(d.B, g);
            if (SIe(d.A.a) == 1) {
                d.c.b = e.R;
                d.c.c = e.S
            }
            d.o = false
        } else if (l3b(d.B, g) && !$re(d.A, e)) {
            Zre(d.A, e);
            if (SIe(d.A.a) == 1) {
                d.c.b = e.R;
                d.c.c = e.S
            }
        }
    }
    o = b.BU(c) & USe;
    c += 2;
    for (s = 0; s < o; s++) {
        g = b.BU(c) & USe;
        c += 2;
        k = E2b(d.e, g);
        !!k && _xe(k)
    }
    d.i && SIe(d.A.a) == 0 && Gxe(d)
}
```
At the end we can see`SIe(d.A.a) == 0`, which checks if the length of the array of player cells is 0, and then shows the game over screen `Gxe(d)` if so. This provideds a fairly comprehensible map for how to parse the node packets.
```js
    m = b.BU(c) & USe;
    c += 2;
    for (j = 0; j < m; ++j) {
        n = E2b(d.e, b.BU(c) & USe);
        H = E2b(d.e, b.BU(c + 2) & USe);
        c += 4;
        if (!!H && !!n && dte) {
            H.g = d.r;
            aye(H, n)
        }
    }
```
This reads the destroyed cells count (`m = b.BU(c) & USe;`) and then iterates through them, reading the destroyer and destroyee ids in turn.
The infinite for loop afterwards reads the updated nodes. It first reads the node_id (and breaks if it's 0), then the x, y, size, and a byte for flags (which is stored as p). A few of these flags aren't really important (e.g. I suspect `v = (p & 1) != 0;` is whether the cell is spiky). p & 2 is a flag for colours, which are packed into two bytes:
```js
        if (t) {
            i = b.BU(c);
            c += 2;
            (!e || e.e != i) && (f = (yre(),
            K = wre[(i & USe & 63488) >> 11],
            L = xre[(i & USe & 2016) >> 5],
            M = wre[i & USe & 31],
            new Ri(K / 255,L / 255,M / 255,1)))
        }
```
The p & 4 indicates whether the cells has a skin (that doesn't match the name) and reads the skin id if so.
The code then reads a null-terminated string, which is the node's name (or 0000 would indicate no name).
p & 0x80 seems to indicate the cell is a player cell (?) and `u = (h & 128) != 0;` seems to check whether the cell is the player's own cell.
Then, after the cells, there is another count and list of ids. Not really sure what this is, but if the player cell id is listed here we have to remove it.

Thus, we can parse the node updates, and respawn the cell when there are no player cells left. (blob.io sometimes fails to respawn, so we then check if we actually spawned and retry if not).

After this, it's a simple matter of hosting a websocket server locally to connect the client a local server, to forward the mouse inputs form the player on to the bots.


