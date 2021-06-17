'use strict';

class Cell extends React.Component {
    constructor(props){
        super(props);

        const segmentation_list = this.props.token["segmentation"];
        let dropdown_list = [];
        for (let i = 0; i < segmentation_list.length; i++) {
            const option = {
                id: i,
                title: segmentation_list[i],
                selected: false,
                key: 'location'
            };
            dropdown_list.push(option);
        }

        const option = {
            id: segmentation_list.length,
            title: "Custom",
            selected: false,
            key: 'location'
        };
        dropdown_list.push(option);


        this.state = {
          location: dropdown_list
        }
    }

    resetThenSet = (id, key) => {
        const temp = [...this.state[key]];
      
        temp.forEach((item) => item.selected = false);
        temp[id].selected = true;
      
        this.setState({
          [key]: temp,
        });
    }

    render() {
        return (
            <div>
                <p>{this.props.token["preferred_segmentation"]}</p>
                <Dropdown  
                    title="Select location"
                    list={this.state.location}
                    resetThenSet={this.resetThenSet}
                />
            </div>
        )
    }
}

class Dropdown extends React.Component {
    constructor(props){
        super(props)
        this.state = {
          isListOpen: false,
          headerTitle: this.props.title
        }
    }

    toggleList = () => {
        this.setState(prevState => ({
          isListOpen: !prevState.isListOpen
       }))
    }

    selectItem = (item) => {
        const { resetThenSet } = this.props;
        const { title, id, key } = item;
      
        this.setState({
          headerTitle: title,
          isListOpen: false,
        }, () => resetThenSet(id, key));
    }

    render() {
        const { isListOpen, headerTitle } = this.state;
        const { list } = this.props;

        return (
          <div className="dd-wrapper">
            <button
              type="button"
              className="dd-header"
              onClick={this.toggleList}
            >
              <div className="dd-header-title">{headerTitle}</div>
              {/* {isListOpen
                ? <FontAwesome name="angle-up" size="2x" />
                : <FontAwesome name="angle-down" size="2x" />} */}
            </button>
            {isListOpen && (
              <div
                role="list"
                className="dd-list"
              >
                {list.map((item) => (
                  <button
                    type="button"
                    className="dd-list-item"
                    key={item.id}
                    onClick={() => this.selectItem(item)}
                  >
                    {item.title}
                    {' '}
                    {/* {item.selected && <FontAwesome name="check" />} */}
                  </button>
                ))}
              </div>
            )}
          </div>
        )
      }
}

class ResultsTable extends React.Component {
    render() {
        let rows = [];
        const tokens_included = this.props.upper_bound - this.props.lower_bound;
        const column_number = (tokens_included >= 10) ? 10 : tokens_included;
        const row_number = Math.ceil(tokens_included/10);
        let current_index = 0;
        // the outer loop will count up to ten, and break if there is less
        for (let i = 0; i < row_number; i++) {
            let row = [];
            for (let j = 0; j < column_number; j++) {
                const current_token = current_index + this.props.lower_bound;
                if (current_token >= this.props.upper_bound) {
                    break;
                }
                row.push(
                    <td key={j}>
                        <Cell token={this.props.data[current_token]}/>
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
            <table id="results_table">
                <tbody>
                    {rows}
                </tbody>
            </table>
        )
    }
}

class Legend extends React.Component {
    render() {
        return (
            <div id="legend">
                <h3>Table Legend</h3>
                <p className="input_token">Input token</p>
                <p> Preferred segmentation</p>
                <p id="segmentation_list_legend">
                    List of n-best segmentations
                </p>
            </div>
        )
    }
}

class PageTableCellButton extends React.Component {
    handleClick() {

    }

    render() {
        return (
            <button 
                className="range_button"
                onClick={() => this.props.onClick(this.props.lower_bound, this.props.upper_bound)}
            >
                {this.props.lower_bound} - {this.props.upper_bound}
            </button>
        )
    }
}

class PageTable extends React.Component {
    /**
     * Displays the results page table that allows to navigate between 
     * results pages (token ranges). 
     */

    render() {
        let rows = [];
        const token_list = this.props.data;
        const token_number = token_list.length;
        const range_rows = Math.ceil(token_number/100);
        const tokens_per_view = 100;
        let current_index = 0;
        for (let i = 0; i < range_rows; i++) {
            const lower_bound = i*tokens_per_view;
            const upper_bound = i != range_rows - 1? (i+1)*tokens_per_view : token_number;
            

        rows.push(
            <tr key={i}>
                <td>
                    <PageTableCellButton 
                        upper_bound={upper_bound} 
                        lower_bound={lower_bound}
                        onClick={(lower_b, upper_b) => this.props.onClick(lower_b, upper_b)}
                    />
                </td>
            </tr>)
    }
        return (
            <table>
                <tbody>
                    {rows}
                </tbody>
            </table>
        )
    }
}



class SideMenu extends React.Component {
    render() {
        return (
            <div>
                <Legend />
                <PageTable 
                    data={this.props.data}
                    onClick={(lower_b, upper_b) => this.props.onClick(lower_b, upper_b)}
                />
                <button id="save_changes_button" className="job_buttons">
                    Save changes
                </button>
            </div>

        );
    }
};

class ResultsSection extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            lower_bound: 0,
            upper_bound: 100,
        }
    }

    handleClick(lower_b, upper_b) {
        this.setState({
            lower_bound: lower_b,
            upper_bound: upper_b,
        });
    }

    render() {
        return (
            <div>
                JobId is {this.props.jobId}
                <SideMenu 
                    data={this.props.data} 
                    onClick={(lower_b, upper_b) => this.handleClick(lower_b, upper_b)}
                />
                <ResultsTable 
                    data={this.props.data} 
                    lower_bound={this.state.lower_bound} 
                    upper_bound={this.state.upper_bound}
                />
            </div>
        )
    }
}

