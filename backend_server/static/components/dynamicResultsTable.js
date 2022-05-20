'use strict';

class DynamicResultsTable extends React.Component {
    render() {
        let rows = [];

        let current_index = this.props.lower_bound;
        while (current_index <= this.props.upper_bound) {
            console.log('Current index');
            console.log(current_index);
            let row = [];
            let total_chars = 0;
            while (total_chars < 60 && row.length < 8) {

                if (current_index >= this.props.upper_bound+1) {
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

                row.push(
                    <div key={current_index} className={cell_sentence_class}>
                        <Cell
                            token={this.props.data[current_index]}
                            show_sentence_number={show_sentence_number}
                            hasSeg={this.props.hasSeg}
                            hasGloss={this.props.hasGloss}
                            index={current_index}
                            updatePreferredSegmentation = {
                                ( index, modelType, newPreferred, isCustom, update_mode) => 
                                this.props.updatePreferredSegmentation(index, modelType, newPreferred, isCustom, update_mode)
                            }
                        />
                    </div>
                )

                if (this.props.data[current_index].hasOwnProperty('preferred_gloss')) {
                    total_chars += this.props.data[current_index].preferred_gloss.length; 
                } else {
                    total_chars += this.props.data[current_index].preferred_segmentation.length;
                }
                current_index++;
            }

            // if there are less than four elements in the row, don't stretch
            const is_short_row = (row.length < 4);
            let filler = [];
            if (is_short_row) {
                filler = Array(8 - row.length).fill().map( () =>
                    {<div className="results_row_short_filler"></div>}
                );
            }

            rows.push(
                <div key={rows.length} className="results_flex_row">
                    {row}
                    {is_short_row && filler}
                </div>
            )
        }

        return (
            <div className="results_wrapper">
                <div id="results_grid">
                    {rows}
                </div>
            </div>
        )
    }
}