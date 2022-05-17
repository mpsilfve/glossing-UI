'use strict';

class ResultsTable extends React.Component {
    render() {
        let rows = [];
        const tokens_included = this.props.upper_bound - this.props.lower_bound + 1;
        const column_number = (tokens_included >= 8) ? 8 : tokens_included;
        const row_number = Math.ceil(tokens_included/10);

        let current_index = 0;
        // the outer loop will count up to (COL LENGTH = 8), and break if there is less
        // 
        for (let i = 0; i < row_number; i++) {
            let row = [];

            for (let j = 0; j < column_number; j++) {
                const current_token = current_index + this.props.lower_bound;
                if (current_token > this.props.upper_bound) {
                    break;
                }
                // TODO why does this render every time
                // console.log(`Lower bound is ${this.props.lower_bound} and current_index is ${current_index} and index is ${current_index + this.props.lower_bound}`)
                
                // assign class to cells based on sentence id to colour different sentences differently in styling
                // odd sentences will get className="odd", and even will get "even".
                let cell_sentence_class = 'odd';
                if (this.props.data[current_token].sentence_id % 2 === 0) {
                    cell_sentence_class = 'even';
                }

                let show_sentence_number = false;
                if (current_token === 0 || this.props.data[current_token].sentence_id != this.props.data[current_token - 1].sentence_id) {
                    show_sentence_number = true;
                }

                row.push(
                    <td key={j} className={cell_sentence_class}>
                        <Cell
                            token={this.props.data[current_token]}
                            show_sentence_number={show_sentence_number}
                            hasSeg={this.props.hasSeg}
                            hasGloss={this.props.hasGloss}
                            index={current_index + this.props.lower_bound}
                            updatePreferredSegmentation = {
                                ( index, modelType, newPreferred, isCustom, update_mode) => 
                                this.props.updatePreferredSegmentation(index, modelType, newPreferred, isCustom, update_mode)
                            }
                        />
                    </td>
                )
                current_index++;
            }
            rows.push(
                <tr key={i}>
                    {row}
                </tr>
            )
        }
        
        return (
            <div className="results_wrapper">
                <table id="results_table">
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        )
    }
}