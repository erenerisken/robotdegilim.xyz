export class Colorset {
  constructor() {
    this.colors = [
      {
        main: "#5FCFEA",
        secondary: "#FFFFFF",
        ternary: "#D0F3FA",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#E669D8",
        secondary: "#FFFFFF",
        ternary: "#F4D1F1",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#F4D35E",
        secondary: "#FFFFFF",
        ternary: "#FAE8A3",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#7FD47F",
        secondary: "#FFFFFF",
        ternary: "#D8F2D8",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#E05656",
        secondary: "#FFFFFF",
        ternary: "#F5BABA",
        text: "#FFFFFF",
        textSection: "#FFFFFF",
      },
      {
        main: "#FFA860",
        secondary: "#FFFFFF",
        ternary: "#FFD4A5",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#A899E2",
        secondary: "#FFFFFF",
        ternary: "#DDD7F7",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#99A3AA",
        secondary: "#FFFFFF",
        ternary: "#D1D6D9",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#60E7CC",
        secondary: "#FFFFFF",
        ternary: "#C5FAF1",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#BEE1E6",
        secondary: "#FFFFFF",
        ternary: "#DAF3F7",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#F4C1F3",
        secondary: "#FFFFFF",
        ternary: "#F9E3F8",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#E5E38B",
        secondary: "#FFFFFF",
        ternary: "#F7F6C3",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#B4E2B4",
        secondary: "#FFFFFF",
        ternary: "#DFF3DF",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#F4A8A8",
        secondary: "#FFFFFF",
        ternary: "#F8D4D4",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#FFC48F",
        secondary: "#FFFFFF",
        ternary: "#FFDEC1",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#B8C5EB",
        secondary: "#FFFFFF",
        ternary: "#DAE0F5",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#CAD6D9",
        secondary: "#FFFFFF",
        ternary: "#E3E9EB",
        text: "#000000",
        textSection: "#FFFFFF",
      },
      {
        main: "#AAEDE2",
        secondary: "#FFFFFF",
        ternary: "#D2F7F2",
        text: "#000000",
        textSection: "#FFFFFF",
      },
    ];

    this.blackDontFill = {
      main: "#000000",
      secondary: "#FFFFFF",
      ternary: "#000000",
      text: "#FFFFFF",
      textSection: "#FFFFFF",
    };
    this.iterator = -1;
  }
  getBlack() {
    return this.blackDontFill;
  }
  getNextColor() {
    if (this.colors.length <= 0) {
      return { main: 0, secondary: 0, ternary: 0 };
    }
    console.log("next color");

    this.iterator = (this.iterator + 1) % this.colors.length;
    return this.colors[this.iterator];
  }

  getPreviousColor() {
    if (this.colors.length <= 0) {
      return { main: 0, secondary: 0, ternary: 0 };
    }
    this.iterator =
      this.iterator > 0 ? this.iterator - 1 : this.colors.length - 1;
    return this.colors[this.iterator];
  }
}
