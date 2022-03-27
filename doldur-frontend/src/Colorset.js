export class Colorset{
    constructor() {
        this.colors = [
            {
                main: "#33CDE8",
                secondary: "#FFFFFF",
                ternary: "#C3F6FF",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#FF38CB",
                secondary: "#FFFFFF",
                ternary: "#F7DCFF",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#FFF040",
                secondary: "#FFFFFF",
                ternary: "#F7F3C2",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#71F154",
                secondary: "#FFFFFF",
                ternary: "#DDF7D7",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#E82A2A",
                secondary: "#FFFFFF",
                ternary: "#FFA9A9",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#FF8F00",
                secondary: "#FFFFFF",
                ternary: "#FFD39A",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#B59FF7",
                secondary: "#FFFFFF",
                ternary: "#E9E2FE",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#8D969A",
                secondary: "#FFFFFF",
                ternary: "#CAD2D5",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#2CFFD9",
                secondary: "#FFFFFF",
                ternary: "#CCFFF6",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#C3F6FF",
                secondary: "#FFFFFF",
                ternary: "#C3F6FF",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#F7DCFF",
                secondary: "#FFFFFF",
                ternary: "#F7DCFF",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#F7F3C2",
                secondary: "#FFFFFF",
                ternary: "#F7F3C2",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#DDF7D7",
                secondary: "#FFFFFF",
                ternary: "#DDF7D7",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#FFA9A9",
                secondary: "#FFFFFF",
                ternary: "#FFA9A9",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#FFD39A",
                secondary: "#FFFFFF",
                ternary: "#FFD39A",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#B6C5FB",
                secondary: "#FFFFFF",
                ternary: "#B6C5FB",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#CAD2D5",
                secondary: "#FFFFFF",
                ternary: "#CAD2D5",
                text: "#000000",
                textSection: "#FFFFFF"
            },
            {
                main: "#CCFFF6",
                secondary: "#FFFFFF",
                ternary: "#CCFFF6",
                text: "#000000",
                textSection: "#FFFFFF"
            },
        ]
        this.blackDontFill = {
            main: "#000000",
            secondary: "#FFFFFF",
            ternary: "#000000",
            text: "#FFFFFF",
            textSection: "#FFFFFF"
        };
        this.iterator = -1;
    }
    getBlack() {
        return this.blackDontFill;
    }
    getNextColor() {
        if (this.colors.length <= 0){
            return {main: 0, secondary: 0, ternary: 0};
        }
        this.iterator = (this.iterator+1)%this.colors.length;
        return this.colors[this.iterator];
    }

    getPreviousColor() {
        if (this.colors.length <= 0){
            return {main: 0, secondary: 0, ternary: 0};
        }
        this.iterator = this.iterator > 0 ? this.iterator - 1 : this.colors.length - 1;
        return this.colors[this.iterator];
    }
}
