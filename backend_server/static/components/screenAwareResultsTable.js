'use strict';

class ScreenAwareResultsTable extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            rows: this.createRows(this.charLimit(), 8)
        };
    }

    componentDidMount() {
        window.addEventListener('resize', this.updateTable);
    }

    componentWillUnmount() {
        window.removeEventListener('resize', this.updateTable);
    }

    componentDidUpdate(prevProps) {
        if (this.props.lower_bound != prevProps.lower_bound || this.props.upper_bound != prevProps.upper_bound ||
                this.props.data != prevProps.data) {
            
            // Don't have to re-calculate in the loading sequence
            const last_prev_token = prevProps.data[prevProps.data.length - 1];
            const last_token = this.props.data[this.props.data.length - 1];

            if (last_prev_token.sentence_id === last_token.sentence_id) {
                this.setState({rows: this.createRows(this.charLimit(), 8)});
            }
        }
    }

    renderCell(cell) {
        return (
            <div key={cell.index} className={cell.sentence_class}>
                <Cell
                    token={cell.token}
                    show_sentence_number={cell.show_number}
                    hasSeg={this.props.hasSeg}
                    hasGloss={this.props.hasGloss}
                    index={cell.index}
                    updatePreferredSegmentation = {
                        (index, modelType, newPreferred, isCustom, update_mode) => 
                        this.props.updatePreferredSegmentation(index, modelType, newPreferred, isCustom, update_mode)
                    }
                />
            </div>
        );
    }

    renderRow(row, key) {
        return(
            <div key={key} className="results_flex_row">
                {row.map(cell => this.renderCell(cell))}
            </div>
        );
    }

    renderTable(rows) {
        return(
            <div className="results_wrapper">
                <div id="results_grid">
                    {rows.map((row, i) => this.renderRow(row, i))}
                </div>
            </div>
        );
    }

    createCellObj(index, token, sentence_class, show_number) {
        return {
            index: index,
            token: token,
            sentence_class: sentence_class,
            show_number: show_number
        };
    }

    createRows(max_chars, max_cols) {
        let rows = [];
        let current_index = this.props.lower_bound;
        while (current_index <= this.props.upper_bound) {
            let row = [];
            let total_chars = 0;
            while (total_chars < max_chars && row.length < max_cols) {
                if (current_index >= this.props.upper_bound + 1) {
                    break;
                }

                // Color the cell blue or purple if it's in an even or odd sentence
                let cell_sentence_class = 'odd';
                if (this.props.data[current_index].sentence_id % 2 === 0) {
                    cell_sentence_class = 'even';
                }

                // If it's the first token in a sentence, show a sentence label
                let show_sentence_number = false;
                if (current_index === 0 || this.props.data[current_index].sentence_id != this.props.data[current_index - 1].sentence_id) {
                    show_sentence_number = true;
                }

                row.push(this.createCellObj(current_index, this.props.data[current_index], cell_sentence_class, show_sentence_number));

                // update total character length for this row
                if (this.props.data[current_index].hasOwnProperty('preferred_gloss')) {
                    total_chars += this.props.data[current_index].preferred_gloss.length; 
                } else {
                    total_chars += this.props.data[current_index].preferred_segmentation.length;
                }

                current_index++;
            }

            rows.push(row);
        }


        return rows;
    }

    updateTable = () => {
        // a simple metric for determining the number of columns in each row: limit the characters to
        // innerWidth / 32 (so 60 characters for a screen size of 1920)
        this.setState({rows: this.createRows(this.charLimit(), 8)});
    }

    charLimit() {
        return Math.ceil(window.innerWidth / 48);
    }

    render() {
        return this.renderTable(this.state.rows);
    }
}