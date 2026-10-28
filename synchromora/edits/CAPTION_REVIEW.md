# Caption review

The burned captions and editable SRT files begin with the source videos' YouTube English **automatic** captions. The cut windows were compared against a separate local faster-whisper `base.en` transcription (the 17 machine outputs are retained in `asr-comparison/`). Two recognizers agreeing is not a substitute for a person listening, especially with overlapping speech, game audio, swearing and noisy livestreams. This is an *automated comparison*, not a human-audio certification.

Corrections made where context or the second pass made the obvious error clear:

- Kai: `cold` → `coal`; `G` → `gift` in the Christmas exchange.
- Jynxzi 2026: `you off on this game` → `you have on this game`.
- Impractical Jokers: `accountable` → `a cannonball`.
- Ronaldo: `Kaisenette` → `Kai Cenat`.
- Jynxzi Live: unreadable overlapping game-commentary words in 224.6–232.1 are labeled `[game commentary]` instead of being fabricated; the truncated `G` at 340.36 becomes `gone`.

The source auto-caption provider replaces some words with `[__]`; the burn-in displays `[…]` rather than pretending to know those words. Captions are supplied as separate SRTs to make corrections easy. The Director should listen and correct them before public posting.
