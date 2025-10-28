# Graph_gen v1.0

import matplotlib.pyplot as plt
import pandas as pd

# ---[Data Preparation Functions]---

def clean_and_prepare_data(df):
    """Clean and prepare the DataFrame for graph generation"""
    if 'Total' in df.columns:
        df = df.drop(columns=['Total'])
    date_column = df.columns[0]
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    df = df.dropna(subset=[date_column])
    df.set_index(date_column, inplace=True)
    return df

def calculate_last_non_zero(df):
    """Calculate the last non-zero values and their corresponding dates"""
    last_non_zero_values = df.apply(lambda x: x[x != 0].iloc[-1] if any(x != 0) else 0)
    last_non_zero_dates = df.apply(lambda x: x[x != 0].last_valid_index())
    last_non_zero_dates = last_non_zero_dates.dropna()
    return last_non_zero_values, last_non_zero_dates

def calculate_days_without_sales(last_non_zero_dates):
    """Calculate the number of days without sales for each agent"""
    today = pd.Timestamp.now().normalize() - pd.Timedelta(days=1)
    days_without_sales = today - last_non_zero_dates
    return days_without_sales.dt.days

# ---[Graph Generation Functions]---

def plot_graph(last_non_zero_values, last_non_zero_dates, days_without_sales, totals, filename, curve_color="red", point_colors=None):
    """Generate and save the KPI graph"""
    plt.figure(figsize=(12, 8))

    # Plot last non-zero values with the specified curve color
    plt.plot(
        last_non_zero_values.index, 
        last_non_zero_dates, 
        color=curve_color, 
        marker='s', 
        markerfacecolor='white', 
        markeredgecolor=curve_color
    )

    # Annotate agents with days without sales
    for agent, date, value, days in zip(
        last_non_zero_values.index, 
        last_non_zero_dates, 
        last_non_zero_values, 
        days_without_sales
    ):
        if pd.notna(date):
            # Determine point color based on days without sales
            if point_colors:
                point_color = point_colors.get(days, "black")  # Default to black if no color is defined
            else:
                point_color = "red"  # Default color if no point_colors are provided

            plt.text(
                agent, date, 
                f'D: {days}', 
                fontsize=10, 
                ha='center', 
                va='bottom', 
                color=point_color, 
                bbox=dict(facecolor='white', edgecolor=point_color, boxstyle='round,pad=0.3')
            )

    # Configure y-axis
    unique_dates = pd.date_range(start=last_non_zero_dates.min(), end=last_non_zero_dates.max(), freq='D')
    plt.gca().set_yticks(unique_dates)
    plt.gca().set_yticklabels(unique_dates.strftime('%Y-%m-%d'))
    plt.gca().invert_yaxis()

    # Annotate total values
    total_line_y = pd.Timestamp.now()
    for agent, value in totals.items():
        plt.text(
            agent, total_line_y, 
            f'Total: {value}', 
            fontsize=10, 
            ha='center', 
            va='bottom', 
            color='blue', 
            bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.3')
        )

    # Add titles and labels
    plt.title(f"KPI for {filename.replace('_', ' ')}")
    plt.xlabel("Sales Agent")
    plt.ylabel("Date")
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.grid(True)

# ---[Main Function]---

def generate_graph(df, filename):
    """Main function to generate and save a KPI graph from a DataFrame"""
    df = clean_and_prepare_data(df)
    totals = df.sum()
    data_without_total = df.drop(index='Total', errors='ignore')
    last_non_zero_values, last_non_zero_dates = calculate_last_non_zero(data_without_total)
    days_without_sales = calculate_days_without_sales(last_non_zero_dates)
    plot_graph(last_non_zero_values, last_non_zero_dates, days_without_sales, totals, filename)

    # Save graph
    output_file = f"kpi_{filename}.png"
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    print(f"Saved {output_file}")
