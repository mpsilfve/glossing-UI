'use strict';

class Cell extends React.Component {
    constructor(props){
        super(props);

        const dropdown_list = this.initilizeList();

        this.state = {
          location: dropdown_list
        }
    }

    initilizeList() {
        console.log(`this: ${this} props: `, this.props);
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

        return dropdown_list;
    }

    changeList(newPreferred, isCustom, update_mode) {
        this.props.updatePreferredSegmentation(this.props.index, newPreferred, isCustom, update_mode);
        this.setState({
            location: this.initilizeList(),
        });
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
                <p>{this.props.token["input"]}</p>
                <p>{this.props.token["preferred_segmentation"]}</p>
                <Dropdown  
                    title={this.props.token["segmentation"][0]}
                    list={this.state.location}
                    resetThenSet={this.resetThenSet}
                    changeList = {(newPreferred, isCustom) => this.changeList(newPreferred, isCustom)}
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
          headerTitle: this.props.title,
          isCustom: false,
          value: '',
        //   set update_mode to default checked radio button value
          selected_update_mode: "only_this",
        };
        // from https://stackoverflow.com/questions/53846717/this-handlechange-this-handlechange-bindthis
        // In JavaScript, class methods are not bound by default. If you forget to bind this.handleClick and 
        // pass it to onClick, this will be undefined when the function is actually called.

        // This is not React-specific behavior; it is a part of how functions work in JavaScript. 
        // Generally, if you refer to a method without () after it, such as onClick={this.handleClick}, you should bind that method.
        
        // If calling bind annoys you, there are two ways you can get around this. you can use 
        // the experimental public class fields syntax or arrow functions in the callback
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleRadioChange = this.handleRadioChange.bind(this);
    }

    static getDerivedStateFromProps(nextProps) {
        const { list, title } = nextProps;
        const selectedItem = list.filter((item) => item.selected);
      
        if (selectedItem.length) {
          return {
            headerTitle: selectedItem[0].title,
          };
        }
        return { headerTitle: title };
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

        // perform update of segmentations
        if (item.title != "Custom") {
            this.props.changeList(item.title, false);
            this.setState(
                {
                    isCustom: false,
                }
            );
        } else {
            this.setState(
                {
                    isCustom: true,
                }
            );
        }
    }

    handleChange(event) {
        this.setState({
            value: event.target.value,
        });
    }

    handleSubmit(event) {
        this.props.changeList(this.state.value, true, this.state.selected_update_mode);
        this.setState({
            value: '',
            isCustom: false,
        });
        event.preventDefault();
    }

    handleRadioChange(event) {
        let update_mode = "all";
        if (event.target.value == "only_this") {
            update_mode = "only_this";
            alert("Only this option is chosen");
        } else if (event.target.value == "all_before") {
            update_mode = "all_before";
            alert("All before option is chosen");
        } else {
            alert("All option is chosen");
        }
        this.setState({
            selected_update_mode: update_mode,
        });
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
              // add custom option if chosen
            )}
            {this.state.isCustom && (
                <form onSubmit={this.handleSubmit}>
                    <input 
                        type="text" 
                        value={this.state.value} 
                        onChange={this.handleChange} 
                        required>
                    </input>
                    <div id="mode_buttons">
                        <input  type="radio" 
                                id="only_this" 
                                name="update_mode" 
                                value="only_this" 
                                checked={this.state.selected_update_mode === "only_this"}
                                onChange={this.handleRadioChange}
                        />
                        <label htmlFor="only_this" className="mode_button">only this</label>
                        <input  type="radio" 
                                id="all_before" 
                                name="update_mode" 
                                value="all" 
                                checked={this.state.selected_update_mode === "all_before"}
                                onChange={this.handleRadioChange}
                        />
                        <label htmlFor="all_before" className="mode_button">all</label>
                        <input  type="radio" 
                                id="all" 
                                name="update_mode" 
                                value="all"
                                checked={this.state.selected_update_mode === "all"}
                                onChange={this.handleRadioChange}
                        />
                        <label htmlFor="all" className="mode_button">all</label>
                    </div>
                    <input type="submit"></input>
                </form>
            )}
          </div>
        )
      }
}


class ResultsTable extends React.Component {
    render() {
        const token_list_length = this.props.data.length;
        let rows = [];
        const upper_bound = token_list_length < 100 ? token_list_length : this.props.upper_bound;
        const tokens_included = upper_bound - this.props.lower_bound;
        const column_number = (tokens_included >= 10) ? 10 : tokens_included;
        const row_number = Math.ceil(tokens_included/10);
        let current_index = 0;
        // the outer loop will count up to ten, and break if there is less
        for (let i = 0; i < row_number; i++) {
            let row = [];
            for (let j = 0; j < column_number; j++) {
                const current_token = current_index + this.props.lower_bound;
                if (current_token >= upper_bound) {
                    break;
                }
                row.push(
                    <td key={j}>
                        <Cell 
                            token={this.props.data[current_token]}
                            index={current_index + this.props.lower_bound}
                            updatePreferredSegmentation = {
                                (index, newPreferred, isCustom, update_mode) => 
                                this.props.updatePreferredSegmentation(index, newPreferred, isCustom, update_mode)
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
            // below is a copy of input data
            data: [...props.data],
        }
    }

    handleClick(lower_b, upper_b) {
        this.setState({
            lower_bound: lower_b,
            upper_bound: upper_b,
        });
    }

    updatePreferredSegmentation(index, newPreferred, isCustom, update_mode) {
        // TODO do something with the update mode
        const newData = [...this.state.data];
        newData[index]["preferred_segmentation"] = newPreferred;

        if (isCustom === true) {
            newData[index]["custom_segmentation"].push(newPreferred);
        }

        this.setState({
            data: newData,
        });
    }

    render() {
        return (
            <div>
                JobId is {this.props.jobId}
                <SideMenu 
                    data={this.state.data} 
                    onClick={(lower_b, upper_b) => this.handleClick(lower_b, upper_b)}
                />
                <ResultsTable 
                    data={this.state.data} 
                    lower_bound={this.state.lower_bound} 
                    upper_bound={this.state.upper_bound}
                    updatePreferredSegmentation = {
                        (index, newPreferred, isCustom, update_mode) => 
                            this.updatePreferredSegmentation(index, newPreferred, isCustom, update_mode)
                    }
                />
            </div>
        )
    }
}

// add sentence indexing
// page table - show number of sentences that fit into 100 tokens
// and do not cut sentence in the middle
// below page add buttons for sentences
// when you hove over these buttons, the sentence cells will
// will highlight.
// when you click on sentence edit button, a window with input sentence will show up
// above the results table with "resubmit" button
// the whole table will then refresh
// how should i hold the data in a JSON object then?
// as token id, you can use sentence id and index within a sentence