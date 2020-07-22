library(shiny)

#DATA
tide <- tide
today <- Sys.time()

#######################################################################################
# Define UI for miles per gallon app ----
ui <- pageWithSidebar(
  
  # App title ----
  headerPanel("Tide Chart Calendar"),
  
  # Sidebar panel for inputs ----
  sidebarPanel(
    
    #LOCATION
    selectInput("location", "Location:", 
                c("Great Hill, MA" = "great-hill-ma")),
    
    #TOGGLES
    checkboxInput("sunset", "Sunset", TRUE),
    checkboxInput("weather", "Weather", TRUE),
    checkboxInput("lunarcal", "Lunar Calendar", TRUE)
  ),
  
  # Main panel for displaying outputs ----
  mainPanel(
    h3(textOutput("tidePlotCaption")),
    
    plotOutput("tidePlot")
  )
)
#######################################################################################




#######################################################################################
# Define server logic to plot various variables against mpg ----
server <- function(input, output) {
  locationInput <- reactive({
    as.character(input$location)
  })
  
  output$tidePlotCaption <- renderText({
    paste("Tide forecast:",input$location)
  }) 
  
  output$tidePlot <- renderPlot({
    wave = tides %>% filter(fullDate >= today & fullDate <= today + 7)
    
  })
}
#######################################################################################



#######################################################################################
shinyApp(ui, server)


