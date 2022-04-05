'use strict';

class PageStepButton extends React.Component {
    constructor(props) {
        super(props);

        this.onClick = this.onClick.bind(this);
    }

    onClick() {
        let to_page;

        // find the previous/next page index (within bounds)
        if (this.props.direction === "prev") {
            to_page = Math.max(this.props.currPage - 1, 0);
        } else {
            to_page = Math.min(this.props.currPage + 1, this.props.pages.length - 1);
        }

        // pass up to PageNav
        let to_page_lower_bound = this.props.pages[to_page].first_token;
        let to_page_upper_bound = this.props.pages[to_page].last_sentence_end;

        return this.props.onClick(to_page_lower_bound, to_page_upper_bound, to_page);
    }

    render() {
        let display_text = (this.props.direction === "prev") ? "<-" : "->";
        
        return (
            <button
                className="range_button"
                onClick={this.onClick}
            >
                {display_text}
            </button>
        );
    }
}


class PageNavButton extends React.Component {
    render() {
        let display_type = (this.props.is_curr_page) ? "curr_page_range_button" : "range_button";
        return (
            <button 
                className={display_type}
                onClick={() => this.props.onClick(this.props.lower_bound, this.props.upper_bound, this.props.page_index)}
            >
                {this.props.page_index + 1}
            </button>
        )
    }
}


class PageNav extends React.Component {
    constructor(props) {
        super(props);
    }

    onClick(lower_b, upper_b, i) {
        this.props.onClick(lower_b, upper_b, i);
    }

    render() {
        const pages = this.props.data;
        let cols = [];

        // first, a prev button, then the page buttons, then a next button
        cols.push(
            <td key="prev">
                <PageStepButton
                    pages={pages}
                    direction="prev"
                    currPage={this.props.currPage}
                    onClick={(lower_b, upper_b, i) => this.onClick(lower_b, upper_b, i)}
                />
            </td>
        );

        for (let i=0; i<pages.length; i++) {
            let is_curr_page = (this.props.currPage === i);
            cols.push(
                <td key={i}>
                    <PageNavButton 
                            lower_bound={pages[i].first_token} 
                            upper_bound={pages[i].last_sentence_end}
                            page_index={i}
                            is_curr_page={is_curr_page}
                            onClick={(lower_b, upper_b, i) => this.onClick(lower_b, upper_b, i)}
                        />
                </td>
            );
        }

        cols.push(
            <td key="next">
                <PageStepButton
                    pages={pages}
                    direction="next"
                    currPage={this.props.currPage}
                    onClick={(lower_b, upper_b, i) => this.onClick(lower_b, upper_b, i)}
                />
            </td>
        );

        return (
            <div className="page_nav_wrapper">
                <table id="page_nav_table">
                    <tbody>
                        <tr>
                            {cols}
                        </tr>
                    </tbody>
                </table>
            </div>
        );
    }
}