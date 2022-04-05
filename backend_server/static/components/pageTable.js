'use strict';

class PageTableCellButton extends React.Component {
    handleClick() {

    }

    render() {
        let display_type = (this.props.is_curr_page) ? "curr_page_range_button" : "range_button";
        return (
            <button 
                className={display_type}
                onClick={() => this.props.onClick(this.props.lower_bound, this.props.upper_bound, this.props.page_index)}
            >
                {this.props.lower_bound} - {this.props.upper_bound}
            </button>
        )
    }
}

class PageTableSentenceButton extends React.Component {
    render() {
        let message;
        if (this.props.annotation_id === null) {
            message = this.props.sentence_id;
        } else {
            message = this.props.annotation_id;
        }
     
        return (
            <button 
                onClick={() => {this.props.onClick(this.props.sentence_id)}}
                className="range_button"
            >
                {message}
            </button>
        )
    }
}


class PageTable extends React.Component {
    /**
     * Displays the results page table that allows to navigate between 
     * results pages (token ranges). 
     */

    constructor(props) {
        super(props);

        console.log(this.props.currPage);

        this.state = {
            sentences_included: this.props.data[0].sentences_included,
            annotations_included: this.props.data[0].annotations_included,
        };
    }

    onClick(lower_b, upper_b, i) {
        this.props.onClick(lower_b, upper_b, i);
        
        let currPage = this.props.currPage;
        this.setState({
            sentences_included: this.props.data[currPage].sentences_included,
            annotations_included: this.props.data[currPage].annotations_included,
        });
    }

    render() {
        const pages = this.props.data;
        let rows = [];
        for (let i = 0; i < pages.length; i++) {
            let is_curr_page = (i === this.props.currPage);
            rows.push(
                <tr key={i}>
                    <td>
                        <PageTableCellButton 
                            lower_bound={pages[i].first_token} 
                            upper_bound={pages[i].last_sentence_end}
                            page_index = {i}
                            is_curr_page = {is_curr_page}
                            onClick={(lower_b, upper_b, i) => this.onClick(lower_b, upper_b, i)}
                        />
                    </td>
                </tr>
            );
        }

        let annotation_present = false;
        let currPage = this.props.currPage;
        let sentences_included = this.props.data[currPage].sentences_included;
        let annotations_included = this.props.data[currPage].annotations_included;

        console.log(sentences_included.length);
        console.log(annotations_included.length);
        if (annotations_included.length === sentences_included.length) {
            annotation_present = true;
        }

        let sentence_rows = [];
        for (let j = 0; j < sentences_included.length; j++) {
            const annotation = annotation_present ? annotations_included[j] : null;
            // console.log(annotation);
            sentence_rows.push(
                <tr key={j}>
                    <td>
                        <PageTableSentenceButton 
                            sentence_id={sentences_included[j]}
                            annotation_id={annotation}
                            onClick={(sentence_id) => {this.props.onRetrieveSentence(sentence_id)}}
                        />
                    </td>
                </tr>
            );
        }

        const unit_type = annotation_present ? 'an annotation' : 'a sentence';

        return (
            <div id="range_table_wrapper">
             <table>
                <tbody>
                    {rows}
                </tbody>
            </table>
            <p>Select {unit_type} to modify:</p>
            <table>
                <tbody>
                    {sentence_rows}
                </tbody>
            </table>
            </div>
        )
    }
}